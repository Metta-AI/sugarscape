"""Adapt a fresh prepared scenario for host JaCaMo and compile its GUI model."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("--java-home", type=Path, required=True)
parser.add_argument("--gradle-home", type=Path, required=True)
parser.add_argument("--gradle-cache", type=Path, required=True)
args = parser.parse_args()
root = args.run.resolve()
assert not (root / "launch.json").exists()
assert not (root / "runtime.json").exists()
config = json.loads((root / "compose.json").read_text())
assert len(config["services"]) == 9
del config["services"]["jacamo"]
(api_port,) = config["services"]["api"]["ports"]
assert api_port["host_ip"] == "127.0.0.1" and api_port["target"] == 5000
model = root / "shared_volume/jacamo/jacamo_model"
changes = json.loads(
    (
        Path(__file__).parent / "results/host-runtime-2026-10-18/host-adaptations.json"
    ).read_text()
)["changes"]
for change in changes:
    path = model / change["file"]
    before = path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == change["before_sha256"]
    old = change["old"]
    new = change["new"] if "hasGUI" in old else f":{api_port['published']}/api/"
    text = before.decode()
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    change.update(new=new, after_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(root / "host-adaptations.json").write_text(
    json.dumps({"changes": changes}, indent=2) + "\n"
)
(root / "compose.json").write_text(json.dumps(config, indent=2) + "\n")
env = os.environ.copy()
env.update(
    JAVA_HOME=str(args.java_home.resolve()),
    GRADLE_USER_HOME=str(args.gradle_cache.resolve()),
)
java = subprocess.run(
    [str(args.java_home / "bin/java"), "-version"],
    capture_output=True,
    text=True,
    check=True,
)
assert 'version "15.0.2"' in java.stderr and "15.0.2+7" in java.stderr
(root / "java-version.txt").write_text(java.stderr)
gradle = str(args.gradle_home.resolve() / "bin/gradle")
version = subprocess.check_output([gradle, "--version"], env=env, text=True)
assert "Gradle 7.4.2" in version
(root / "gradle-version.txt").write_text(version)
with (root / "host-compile.log").open("x") as stream:
    subprocess.run(
        [gradle, "--no-daemon", "--no-watch-fs", "--console=plain", "classes"],
        cwd=model,
        env=env,
        stdout=stream,
        stderr=subprocess.STDOUT,
        check=True,
        timeout=600,
    )
(root / "runtime.json").write_text(
    json.dumps(
        {
            "java_home": str(args.java_home.resolve()),
            "gradle_home": str(args.gradle_home.resolve()),
            "gradle_cache": str(args.gradle_cache.resolve()),
            "java_version": "15.0.2+7",
            "gradle_version": "7.4.2",
            "simulation_started": False,
        },
        indent=2,
    )
    + "\n"
)
subprocess.run(
    ["docker", "compose", "-f", str(root / "compose.json"), "config", "--quiet"],
    check=True,
)
