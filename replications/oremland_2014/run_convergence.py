"""Run the frozen convergence shards with bounded native NetLogo workers."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("java_home", type=Path)
parser.add_argument("netlogo_app", type=Path)
parser.add_argument("model", type=Path)
parser.add_argument("experiment", type=Path)
parser.add_argument("--timeout", type=Path, required=True)
args = parser.parse_args()
root = args.experiment.resolve()
protocol = json.loads((root / "protocol.json").read_text())
assert protocol["workers"] == 4 and protocol["runs"] == 20000
assert protocol["maximum_seconds_per_worker"] == 1800
for name, digest in protocol["files_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
run = root / "execution"
run.mkdir(exist_ok=False)
source = Path(__file__).with_name("RunPolicyBatch.java")
(run / source.name).write_bytes(source.read_bytes())
(run / "oremland.nlogo").write_bytes(args.model.read_bytes())
landscape = args.model.with_name("sugar-map.txt")
assert (
    hashlib.sha256(landscape.read_bytes()).hexdigest()
    == "cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675"
)
(run / "sugar-map.txt").write_bytes(landscape.read_bytes())
config = (args.netlogo_app / "NetLogo.cfg").read_text().splitlines()
assert "app.version=5.3.1" in config
names = next(
    line.split("=", 1)[1] for line in config if line.startswith("app.classpath=")
).split(":")
jars = [args.netlogo_app / name for name in ["NetLogo.jar", *names]]
classpath = ":".join(str(path.resolve()) for path in jars) + ":" + str(run)
compile_command = [
    str(args.java_home / "bin/javac"),
    "-cp",
    classpath,
    "-d",
    str(run),
    str(run / source.name),
]
subprocess.run(compile_command, check=True)
command = [
    str(args.timeout),
    "--signal=TERM",
    "--kill-after=30",
    "1800",
    str(args.java_home / "bin/java"),
    "-Xmx512m",
    "-XX:ActiveProcessorCount=1",
    "-Djava.awt.headless=true",
    "-Dfile.encoding=UTF-8",
    "-cp",
    classpath,
    "RunPolicyBatch",
    str(run / "oremland.nlogo"),
]
manifest = {
    "started_unix": time.time(),
    "launcher_pid": os.getpid(),
    "compile_command": compile_command,
    "command_prefix": command,
    "java_version": subprocess.check_output(
        [str(args.java_home / "bin/java"), "-version"],
        stderr=subprocess.STDOUT,
        text=True,
    ),
    "sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [
            root / "protocol.json",
            run / source.name,
            run / "RunPolicyBatch.class",
            run / "oremland.nlogo",
            run / "sugar-map.txt",
            Path(__file__),
        ]
    },
    "jars": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in jars
        if path.is_file()
    },
    "missing_declared_jars": [path.name for path in jars if not path.is_file()],
}
(run / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def execute(worker):
    """Execute one disjoint shard and preserve its terminal status."""
    invocation = [
        *command,
        str(root / f"requests-{worker}.jsonl"),
        str(run / f"results-{worker}.jsonl"),
    ]
    started = time.time()
    with (run / f"worker-{worker}.log").open("x") as stream:
        process = subprocess.Popen(invocation, stdout=stream, stderr=subprocess.STDOUT)
        (run / f"worker-{worker}.json").write_text(
            json.dumps(
                {"pid": process.pid, "started_unix": started, "command": invocation},
                indent=2,
            )
            + "\n"
        )
        code = process.wait()
    (run / f"exit-{worker}.json").write_text(
        json.dumps(
            {"exit_code": code, "elapsed_seconds": time.time() - started}, indent=2
        )
        + "\n"
    )
    return code


with ThreadPoolExecutor(max_workers=4) as executor:
    codes = list(executor.map(execute, range(4)))
(run / "exit.json").write_text(
    json.dumps(
        {
            "exit_codes": codes,
            "elapsed_seconds": time.time() - manifest["started_unix"],
        },
        indent=2,
    )
    + "\n"
)
assert codes == [0, 0, 0, 0], codes
