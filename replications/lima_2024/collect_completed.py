"""Back up completed trajectories before reading the stopped native database."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert json.loads((args.run / "terminal.json").read_text())["containers_stopped"]
compose = ["docker", "compose", "-f", str(args.run / "compose.json")]
states = subprocess.run(
    [*compose, "ps", "-a", "--format", "json"],
    capture_output=True,
    text=True,
    check=True,
)
containers = [json.loads(line) for line in states.stdout.splitlines()]
assert containers and all(row["State"] == "exited" for row in containers)
(database,) = [row["ID"] for row in containers if row["Service"] == "db"]
files = [
    args.run / f"shared_volume/netlogo_output/{model}_{kind}.txt"
    for model in ("m1", "m2")
    for kind in ("output", "alive")
]
files += sorted(
    (args.run / "shared_volume/jacamo/jacamo_model/src/agt/list").glob("*.asl")
)
hashes = {
    str(path.relative_to(args.run)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in files
}
args.output.mkdir()
with tarfile.open(
    args.output / "native-files-before-db-start.tar.gz", "x:gz"
) as archive:
    for path in files:
        archive.add(path, arcname=str(path.relative_to(args.run)), recursive=False)
(args.output / "native-files-sha256.json").write_text(
    json.dumps(hashes, indent=2) + "\n"
)
sql = "SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ; START TRANSACTION WITH CONSISTENT SNAPSHOT;\n"
for table in ("m1", "m2", "m3", "router"):
    fields = (
        "id",
        "agent_id",
        "data",
        "path",
        "asl_file_path",
        "processed",
        "created_at",
        "updated_at",
    )
    pairs = ",".join(f"'{field}',{field}" for field in fields)
    sql += f"SELECT JSON_OBJECT('table','{table}',{pairs}) FROM {table} ORDER BY id;\n"
sql += "COMMIT;\n"
# Compose start traverses dependencies, including destructive clear_files.
# Start the already identified database container directly instead.
subprocess.run(["docker", "start", database], check=True)
try:
    for attempt in range(30):
        ready = subprocess.run(
            ["docker", "exec", database, "mysqladmin", "-uroot", "-proot", "ping"],
            capture_output=True,
        )
        if ready.returncode == 0:
            break
        time.sleep(1)
    assert ready.returncode == 0
    with (args.output / "snapshot-final.jsonl").open("xb") as stream:
        subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                database,
                "mysql",
                "-uroot",
                "-proot",
                "--batch",
                "--raw",
                "--skip-column-names",
                "MYSQL_DATABASE",
            ],
            input=sql.encode(),
            stdout=stream,
            check=True,
        )
finally:
    subprocess.run(["docker", "stop", database], check=True)
assert all(
    hashlib.sha256((args.run / name).read_bytes()).hexdigest() == digest
    for name, digest in hashes.items()
)
after = subprocess.run(
    [*compose, "ps", "-a", "--format", "json"],
    capture_output=True,
    text=True,
    check=True,
)
assert all(json.loads(line)["State"] == "exited" for line in after.stdout.splitlines())
(args.output / "terminal-containers.jsonl").write_text(after.stdout)
