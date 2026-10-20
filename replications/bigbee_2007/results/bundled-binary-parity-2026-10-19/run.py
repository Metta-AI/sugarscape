"""Replay original bundled binary classes without rebuilding author sources."""

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tarfile
import time

root = Path(__file__).resolve().parent
repo = root.parent.parent / "sugarscape-bigbee/replications/bigbee_2007"
archive = root.parent / "papers/mason_sugarscape_1.1.2.tar.gz"
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == "837e4fd1d64c54c5587a7a5ce11a262bdf9cead4c982e6bc778468368e32d514"
)
assert shutil.disk_usage(root).free > 256 * 1024**2
native = root / "native"
native.mkdir()
files = {}
with tarfile.open(archive) as t:
    for member in t:
        assert member.isdir() or member.isfile()
        assert (
            not Path(member.name).is_absolute() and ".." not in Path(member.name).parts
        )
        if member.isfile():
            body = t.extractfile(member).read()
            path = native / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            files[member.name] = {
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "archive_mtime": member.mtime,
            }
engine = native / "mason_sugarscape_1.1"
classes = root / "wrappers"
classes.mkdir()
empty = root / "empty-sourcepath"
empty.mkdir()
jdk = Path("/opt/homebrew/opt/openjdk@11/bin")
command = [
    str(jdk / "javac"),
    "-sourcepath",
    str(empty),
    "-cp",
    str(engine) + ":" + str(engine / "lib/*"),
    "-d",
    str(classes),
    str(repo / "Replay.java"),
    str(repo / "AuditReplay.java"),
]
p = subprocess.run(command, capture_output=True, text=True, timeout=120)
(root / "compile.json").write_text(
    json.dumps(
        {
            "command": command,
            "exit_code": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        },
        indent=2,
    )
    + "\n"
)
assert p.returncode == 0, p.stderr
assert sorted(p.name for p in classes.rglob("*.class")) == [
    "AuditReplay.class",
    "Replay.class",
]
manifest = {
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "files": files,
    "wrapper_sha256": {
        n: hashlib.sha256((repo / n).read_bytes()).hexdigest()
        for n in ["Replay.java", "AuditReplay.java"]
    },
    "java_version": subprocess.check_output(
        [str(jdk / "java"), "-version"], stderr=subprocess.STDOUT, text=True
    ).strip(),
    "scope": "Bundled author model/framework bytecode only. Empty compiler sourcepath and exactly two newly compiled wrapper classes. Archive timestamps are metadata, not proof of historical experiment identity.",
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
receipts = []
for config in ["anim2-3", "fig3-4", "fig3-5"]:
    for repeat in ["a", "b", "observer"]:
        stem = config + "-" + repeat
        kind = "AuditReplay" if repeat == "observer" else "Replay"
        command = [
            str(jdk / "java"),
            "-Djava.awt.headless=true",
            "-Xlog:class+load=info:file=" + str(root / (stem + ".classes.log")),
            "-cp",
            str(classes) + ":" + str(engine) + ":" + str(engine / "lib/*"),
            kind,
            "conf/" + config + ".conf",
            "0",
            "1000",
        ]
        if repeat == "observer":
            command.append(str(root / (stem + "-population.csv")))
        started = time.monotonic()
        with (
            (root / (stem + ".stdout")).open("x") as out,
            (root / (stem + ".stderr")).open("x") as err,
        ):
            p = subprocess.run(command, cwd=engine, stdout=out, stderr=err, timeout=120)
        receipt = {
            "configuration": config,
            "repeat": repeat,
            "command": command,
            "exit_code": p.returncode,
            "elapsed_seconds": time.monotonic() - started,
        }
        (root / (stem + ".terminal.json")).write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        receipts.append(receipt)
        assert p.returncode == 0, stem
        print(stem, "exit0", flush=True)
for name, expected in files.items():
    if name.endswith((".class", ".java", ".jar", ".conf")):
        assert (
            hashlib.sha256((native / name).read_bytes()).hexdigest()
            == expected["sha256"]
        )
(root / "runs.json").write_text(json.dumps(receipts, indent=2) + "\n")
print("All bundled-binary runs complete; scientific comparison pending", flush=True)
