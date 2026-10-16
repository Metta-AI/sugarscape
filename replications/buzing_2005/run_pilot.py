"""Compile the archived release and run its defaults for 100 cycles."""

import argparse
import hashlib
import math
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from pydantic import BaseModel


class Manifest(BaseModel):
    archive_sha256: str
    adapter_sha256: str
    source_count: int
    java_version: str
    command: list[str]
    configuration_sha256: dict[str, str]
    output_sha256: dict[str, str]
    scalar_observations: int
    final_population: int
    status: str = "Operational pilot; not a paper replication"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("java_home", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
archive = args.archive.resolve()
java_home = args.java_home.resolve()
output = args.output.resolve()
archive_hash = digest(archive)
assert archive_hash == "f60a4fc96a419bbb72fe51990893f93cda5ff86f1b5668f9ffe887303ebed2e2"
output.mkdir(parents=True, exist_ok=False)
with zipfile.ZipFile(archive) as bundle:
    assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in bundle.namelist())
    bundle.extractall(output / "reference")
reference = output / "reference" / "JAWAS"
classes = output / "classes"
classes.mkdir()
sources = sorted(
    path
    for package in ("model", "data", "util", "experiments")
    for path in (reference / "src/nl/vu/cs/sugarland" / package).rglob("*.java")
)
assert len(sources) == 78
with (output / "compile.log").open("w") as log:
    subprocess.run(
        [str(java_home / "bin/javac"), "-encoding", "ISO-8859-1", "-cp", str(reference / "lib"),
         "-d", str(classes), *map(str, sources)],
        stdout=log, stderr=subprocess.STDOUT, check=True,
    )
shutil.copytree(reference / "lib/config", output / "config")
experiment = output / "config/Experiment/experiment.cfg"
settings = experiment.read_text()
for key, value in (("useGui", "false"), ("numberOfRuns", "1"), ("runLength", "100")):
    settings, replacements = re.subn(rf"(?m)^{key}\s*=.*$", f"{key} = {value}", settings)
    assert replacements <= 1
    if replacements == 0:
        settings += f"\n{key} = {value}\n"
experiment.write_text(settings)
with (output / "config/Scape/scape.cfg").open("a") as config:
    config.write("\nrandomSeed = 0\n")
adapter = Path(__file__).with_name("Replay.java").resolve()
command = [str(java_home / "bin/java"), "-Djava.awt.headless=true", "-cp",
           f"{classes}:{reference / 'lib'}", str(adapter)]
with (output / "run.log").open("w") as log:
    subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=90)
observations = 0
for path in sorted((output / "data").glob("*.avg")):
    rows = [line.split() for line in path.read_text().splitlines()]
    assert len(rows) == 100 and all(len(row) == 2 for row in rows), path
    assert [int(row[0]) for row in rows] == list(range(100)), path
    assert all(math.isfinite(float(row[1])) for row in rows), path
    observations += len(rows)
assert observations == 700
population = output / "data/experiment_0_.numberOfAgents.avg"
final_population = float(population.read_text().splitlines()[-1].split()[1])
assert final_population.is_integer() and final_population > 0
assert f"iterations=100,initial=1000,final={int(final_population)}" in (output / "run.log").read_text()
manifest = Manifest(
    archive_sha256=archive_hash, adapter_sha256=digest(adapter), source_count=len(sources),
    java_version=subprocess.run([str(java_home / "bin/java"), "-version"], capture_output=True, text=True, check=True).stderr,
    command=command,
    configuration_sha256={str(path.relative_to(output)): digest(path) for path in sorted((output / "config").rglob("*.cfg"))},
    output_sha256={str(path.relative_to(output)): digest(path) for path in sorted((output / "data").iterdir())},
    scalar_observations=observations, final_population=int(final_population),
)
(output / "manifest.json").write_text(manifest.model_dump_json(indent=2) + "\n")
print(manifest.model_dump_json(indent=2))
