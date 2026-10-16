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
    variant: str
    seed: int
    cycles: int
    threshold: int
    source_sha256: dict[str, str]
    seed_control_replacements: dict[str, int]
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
parser.add_argument("variant", choices=["original", "controlled", "balanced-landscape", "paper-harvest", "paper-com1", "paper-com0", "paper-com2"])
parser.add_argument("seed", type=int)
parser.add_argument("--threshold", type=int, choices=range(5), default=1)
parser.add_argument("--cycles", type=int, default=100)
args = parser.parse_args()
assert 1 <= args.cycles <= 5000
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
seed_replacements = {}
if args.variant in ("controlled", "balanced-landscape", "paper-harvest", "paper-com1", "paper-com0", "paper-com2"):
    for source in sources:
        data = source.read_bytes()
        count = data.count(b"new Random()")
        if count:
            seed_replacements[str(source.relative_to(reference))] = count
            source.write_bytes(data.replace(b"new Random()", b"nl.vu.cs.sugarland.util.ReplicationRandom.create()"))
    assert sum(seed_replacements.values()) == 7 and len(seed_replacements) == 4
    sources.append(Path(__file__).with_name("ReplicationRandom.java").resolve())
if args.variant in ("balanced-landscape", "paper-harvest", "paper-com1", "paper-com0", "paper-com2"):
    source = reference / "src/nl/vu/cs/sugarland/model/SugarScape.java"
    data = source.read_text(encoding="latin-1")
    start = data.index("            while (numberOfSeeds > 0)")
    stop = data.index("        else if (intProps[SUGAR_DISTRIBUTION_UNIF] == 2)", start)
    data = data[:start] + """            int sizeSum = intProps[MAX_SUGAR_SIZE] * (intProps[MAX_SUGAR_SIZE] + 1) / 2;
            if (numberOfSeeds % sizeSum != 0) throw new IllegalArgumentException("Unbalanced seed budget");
            int seedsPerSize = numberOfSeeds / sizeSum;
            for (size = 1; size <= intProps[MAX_SUGAR_SIZE]; size++)
            {
                for (int count = 0; count < seedsPerSize; count++)
                {
                    if (numberOfSeedsToDistribute >= sugarSeedsToDistribute.length) doubleSugarSeedArray();
                    sugarSeedsToDistribute[numberOfSeedsToDistribute++] =
                        new SugarSeed((float) size, (float) size, floatProps[SUGAR_GROWBACK_RATE]);
                }
            }
        }
""" + data[stop:]
    source.write_text(data, encoding="latin-1")
if args.variant in ("paper-harvest", "paper-com1", "paper-com0", "paper-com2"):
    source = reference / "src/nl/vu/cs/sugarland/model/SugarAgent.java"
    data = source.read_text(encoding="latin-1")
    old = "        // if more than one agent on cell, then evenly divide sugar\n        if (agentsOnCell.length > 1)"
    new = """        // Reconstructed paper rule: accessible piles are eaten alone first.
        float[] priorSugar = new float[agentsOnCell.length];
        for (int i = 0; i < agentsOnCell.length; i++) priorSugar[i] = agentsOnCell[i].floatProps[SUGAR_AMOUNT];
        if (agentsOnCell.length > 1 && localAmount > intProps[MAX_SUGAR_HARVEST])"""
    assert data.count(old) == 1
    data = data.replace(old, new)
    marker = "        // flow of control will only come here if sugar has been eaten during this method invocation"
    audit = """        if (agentsOnCell.length > 1)
        {
            for (int i = 0; i < agentsOnCell.length; i++)
            {
                float gain = localAmount > intProps[MAX_SUGAR_HARVEST] ? localAmount / (float) agentsOnCell.length : (agentsOnCell[i] == this ? localAmount : 0);
                float expected = priorSugar[i] + gain;
                if (agentsOnCell[i].floatProps[SUGAR_AMOUNT] != expected)
                    throw new IllegalStateException("Paper harvest allocation violated");
            }
            System.out.println("paper-harvest-verified amount=" + localAmount + ",agents=" + agentsOnCell.length + ",shared=" + (localAmount > intProps[MAX_SUGAR_HARVEST]));
        }

"""
    assert data.count(marker) == 1
    source.write_text(data.replace(marker, audit + marker), encoding="latin-1")
if args.variant == "paper-com1":
    source = reference / "src/nl/vu/cs/sugarland/model/SugarAgent.java"
    data = source.read_text(encoding="latin-1")
    start = data.index("    private CellValueInformation listenToDirection(int dir)")
    stop = data.index("    public ", start)
    section = data[start:stop]
    marker = "                    if (i == null) continue;"
    assert section.count(marker) == 4
    section = section.replace(marker, marker + """
                    if (messageBoard.getRemoveAfterListening())
                    {
                        if (messageBoard.getMessage(i.getXcoordinate(), i.getYcoordinate()) != null)
                            throw new IllegalStateException("COM1 read did not consume message");
                        System.out.println("paper-com1-read-verified");
                    }""")
    data = data[:start] + section + data[stop:]
    old = "            if (messageBoard.getRemoveAfterListening()) messageBoard.deleteMessage(xBest, yBest);"
    assert data.count(old) == 1
    source.write_text(data, encoding="latin-1")
with (output / "compile.log").open("w") as log:
    subprocess.run(
        [str(java_home / "bin/javac"), "-encoding", "ISO-8859-1", "-cp", str(reference / "lib"),
         "-d", str(classes), *map(str, sources)],
        stdout=log, stderr=subprocess.STDOUT, check=True,
    )
shutil.copytree(reference / "lib/config", output / "config")
experiment = output / "config/Experiment/experiment.cfg"
settings = experiment.read_text()
for key, value in (("useGui", "false"), ("numberOfRuns", "1"), ("runLength", str(args.cycles))):
    settings, replacements = re.subn(rf"(?m)^{key}\s*=.*$", f"{key} = {value}", settings)
    assert replacements <= 1
    if replacements == 0:
        settings += f"\n{key} = {value}\n"
experiment.write_text(settings)
with (output / "config/Scape/scape.cfg").open("a") as config:
    config.write(f"\nrandomSeed = {args.seed}\n")
if args.variant in ("balanced-landscape", "paper-harvest", "paper-com1", "paper-com0", "paper-com2"):
    scape_config = output / "config/Scape/scape.cfg"
    settings, replacements = re.subn(r"(?m)^sugarRichness\s*=.*$", "sugarRichness = 1.0f", scape_config.read_text())
    assert replacements == 1
    scape_config.write_text(settings)
if args.variant in ("paper-com0", "paper-com1", "paper-com2"):
    overrides = {
        "Experiment/experiment.cfg": {"nrOfSubcycles": "1"},
        "Agent/agent.cfg": {"minInitialSugar": "0", "maxReproductionSugar": "0", "mutationSigma": "0.1",
                            "mutationOperator.listenPref": str(args.variant != "paper-com0").lower(),
                            "mutationOperator.talkPref": str(args.variant != "paper-com0").lower(),
                            "maxSugarHarvest": str(args.threshold)},
        "Scape/scape.cfg": {"message.removeAfterNIterations": "0", "message.removeAfterListening": str(args.variant == "paper-com1").lower(),
                            "message.removeAfterResponse": str(args.variant == "paper-com2").lower()},
    }
    if args.variant == "paper-com0":
        overrides["Agent/agent.cfg"].update(minListenPref="0", maxListenPref="0", minTalkPref="0", maxTalkPref="0")
    for relative, changes in overrides.items():
        config = output / "config" / relative
        settings = config.read_text()
        for key, value in changes.items():
            settings, replacements = re.subn(rf"(?m)^{re.escape(key)}\s*=.*$", f"{key} = {value}", settings)
            assert replacements == 1, key
        config.write_text(settings)
adapter = Path(__file__).with_name("Replay.java").resolve()
command = [str(java_home / "bin/java"), "-Djava.awt.headless=true", f"-Dreplication.seed={args.seed}", "-cp",
           f"{classes}:{reference / 'lib'}", str(adapter)]
with (output / "run.log").open("w") as log:
    subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=3660)
observations = 0
for path in sorted((output / "data").glob("*.avg")):
    rows = [line.split() for line in path.read_text().splitlines()]
    assert len(rows) == args.cycles and all(len(row) == 2 for row in rows), path
    assert [int(row[0]) for row in rows] == list(range(args.cycles)), path
    assert all(math.isfinite(float(row[1])) for row in rows), path
    observations += len(rows)
assert observations == 7 * args.cycles
population = output / "data/experiment_0_.numberOfAgents.avg"
final_population = float(population.read_text().splitlines()[-1].split()[1])
assert final_population.is_integer() and final_population >= 0
assert f"iterations={args.cycles},initial=1000,final={int(final_population)}" in (output / "run.log").read_text()
manifest = Manifest(
    variant=args.variant, seed=args.seed, cycles=args.cycles, threshold=args.threshold, source_sha256={str(path): digest(path) for path in sources},
    seed_control_replacements=seed_replacements,
    archive_sha256=archive_hash, adapter_sha256=digest(adapter), source_count=len(sources),
    java_version=subprocess.run([str(java_home / "bin/java"), "-version"], capture_output=True, text=True, check=True).stderr,
    command=command,
    configuration_sha256={str(path.relative_to(output)): digest(path) for path in sorted((output / "config").rglob("*.cfg"))},
    output_sha256={str(path.relative_to(output)): digest(path) for path in sorted((output / "data").iterdir())},
    scalar_observations=observations, final_population=int(final_population),
)
(output / "manifest.json").write_text(manifest.model_dump_json(indent=2) + "\n")
print(manifest.model_dump_json(indent=2))
