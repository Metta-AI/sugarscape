"""Prepare an isolated all-container experiment from the pinned author checkout."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("netlogo_archive", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("--project", required=True)
parser.add_argument("--port-offset", type=int, default=20000)
args = parser.parse_args()
assets = Path(__file__).parent
pins = json.loads((assets / "source-pins.json").read_text())
assert re.fullmatch(r"sugarscape-lima-[a-z0-9-]+", args.project)
assert 1024 <= args.port_offset + 80 < args.port_offset + 9906 <= 65535
assert (
    subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    == pins["revision"]
)
assert not subprocess.check_output(
    ["git", "-C", str(args.source), "status", "--porcelain"], text=True
).strip()
for name, digest in pins["files"].items():
    assert hashlib.sha256((args.source / name).read_bytes()).hexdigest() == digest
archive_hash = "0dcd9df4dfb218826a74f9df42163fa588908a1dfe58864106936f8dfb76acec"
assert hashlib.sha256(args.netlogo_archive.read_bytes()).hexdigest() == archive_hash
args.run.mkdir()
root = args.run.resolve()
shutil.copytree(args.source / "shared_volume", root / "shared_volume")
for dockerfile in args.source.glob("Dockerfile_*"):
    shutil.copyfile(dockerfile, root / dockerfile.name)
shutil.copyfile(args.netlogo_archive, root / "NetLogo-6.0.4-64.tgz")
shutil.copyfile(assets / "Dockerfile_NETLOGO", root / "Dockerfile_NETLOGO")
original = subprocess.check_output(
    [
        "docker",
        "compose",
        "-f",
        str(args.source / "docker-compose-local.yaml"),
        "config",
        "--format",
        "json",
    ],
)
config = json.loads(original)
(root / "original-compose.json").write_bytes(original)
config["name"] = args.project
config["networks"]["my_network"]["name"] = args.project
for name, service in config["services"].items():
    del service["container_name"]
    service.pop("restart", None)
    service["build"]["context"] = str(root)
    service["platform"] = "linux/amd64"
    service["mem_limit"] = (
        "1536m" if name in ("jacamo", "modelo_1", "modelo_2") else "512m"
    )
    service["cpus"] = 1
    for volume in service.get("volumes", []):
        assert volume["type"] == "bind"
        volume["source"] = str(
            root / Path(volume["source"]).relative_to(args.source.resolve())
        )
    for port in service.get("ports", []):
        port["host_ip"] = "127.0.0.1"
        port["published"] = str(int(port["published"]) + args.port_offset)
(root / "compose.json").write_text(json.dumps(config, indent=2) + "\n")
(root / "preparation.json").write_text(
    json.dumps(
        {
            "revision": pins["revision"],
            "project": args.project,
            "netlogo_archive_sha256": archive_hash,
            "netlogo_dockerfile_sha256": hashlib.sha256(
                (root / "Dockerfile_NETLOGO").read_bytes()
            ).hexdigest(),
            "model_source_changes": [],
            "memory_limit_mib": 7680,
            "runtime_equivalence": "Historical dependency equivalence unproven; replacement runtime disclosed.",
        },
        indent=2,
    )
    + "\n"
)
subprocess.run(
    ["docker", "compose", "-f", str(root / "compose.json"), "config", "--quiet"],
    check=True,
)
print(root / "compose.json")
