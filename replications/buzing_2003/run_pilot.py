"""Run the distinct 2003 VUScape protocol from hash-verified recovered native sources."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference_run", type=Path, help="Audited 2005 paper-com2 reconstruction used only as source/configuration preparation")
parser.add_argument("output", type=Path)
parser.add_argument("policy", choices=("none", "read", "response", "expiry-one"))
parser.add_argument("threshold", type=int, choices=range(5))
parser.add_argument("seed", type=int)
parser.add_argument("--reproduction", choices=("specified", "released"), default="specified")
parser.add_argument("--subcycles", type=int, choices=(1, 2), default=1)
args = parser.parse_args()
reference = args.reference_run.resolve()
manifest = json.loads((reference / "manifest.json").read_text())
assert manifest["variant"] == "paper-com2" and manifest["unpaced"]
assert manifest["archive_sha256"] == "f60a4fc96a419bbb72fe51990893f93cda5ff86f1b5668f9ffe887303ebed2e2"
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
for name, checksum in manifest["configuration_sha256"].items():
    assert hashlib.sha256((reference / name).read_bytes()).hexdigest() == checksum
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
shutil.copytree(reference / "config", output / "config")
communicating = args.policy != "none"
overrides = {
    "Experiment/experiment.cfg": {"runLength": "500", "numberOfRuns": "1", "nrOfSubcycles": str(args.subcycles)},
    "Scape/scape.cfg": {"initialPopulation": "400", "sugarRichness": "0.5", "sugarGrowBackRate": "3.0",
                        "randomSeed": str(args.seed), "message.removeAfterNIterations": "1" if args.policy == "expiry-one" else "0",
                        "message.removeAfterListening": str(args.policy == "read").lower(),
                        "message.removeAfterResponse": str(args.policy == "response").lower()},
    "Agent/agent.cfg": {"minInitialSugar": "50", "maxInitialSugar": "50", "minReproductionSugar": "5", "maxReproductionSugar": "5",
                        "mutationSigma": "0.01", "mutationOperator.listenPref": "false", "mutationOperator.talkPref": str(communicating).lower(),
                        "minListenPref": str(int(communicating)), "maxListenPref": str(int(communicating)),
                        "minTalkPref": "0", "maxTalkPref": str(int(communicating)), "maxSugarHarvest": str(args.threshold)},
}
for name, changes in overrides.items():
    path = output / "config" / name
    data = path.read_text()
    for key, value in changes.items():
        data, count = re.subn(rf"(?m)^{re.escape(key)}\s*=.*$", f"{key} = {value}", data)
        assert count == 1, key
    path.write_text(data)
sources = [Path(name) for name in manifest["source_sha256"]]
source = next(p for p in sources if p.name == "SugarAgent.java")
data = source.read_text(encoding="latin-1")
if args.reproduction == "specified":
    for bound, operator in (("BEGIN_CHILD_BEARING_AGE", "<"), ("END_CHILD_BEARING_AGE", ">")):
        old = f"if (a.getAge() {operator} intProps[{bound}]) continue;"
        assert data.count(old) == 1
        data = data.replace(old, f"if (a.getAge() {operator} a.intProps[{bound}]) continue;")
    for old in ("if (floatProps[SUGAR_AMOUNT] < intProps[MIN_REPRODUCTION_SUGAR]) return;",
                "if (a.floatProps[SUGAR_AMOUNT] < a.intProps[MIN_REPRODUCTION_SUGAR]) continue;"):
        assert data.count(old) == 1
        data = data.replace(old, old.replace(" < ", " <= "))
    # Reproduction can visit several partners; earlier births can lower the initiator below five sugar.
    marker = "            partner = (SugarAgent) e.nextElement();"
    assert data.count(marker) == 1
    data = data.replace(marker, marker + """
                if (floatProps[SUGAR_AMOUNT] <= intProps[MIN_REPRODUCTION_SUGAR]) return;
                if (partner.floatProps[SUGAR_AMOUNT] <= partner.intProps[MIN_REPRODUCTION_SUGAR]) continue;
    """)
if not communicating:
    for gene in ("TALK_PREF", "LISTEN_PREF"):
        old = f"rand.getFloat() <= floatProps[{gene}]"
        assert data.count(old) == 1
        data = data.replace(old, "rand.getFloat() < 0.0f")
marker = "            floatProps[SUGAR_AMOUNT] /= 2.0f;"
assert data.count(marker) == 1
observer = '            System.out.println("birth2003," + scape.getIteration() + "," + floatProps[SUGAR_AMOUNT] + "," + partner.floatProps[SUGAR_AMOUNT]);\n'
observer += '            System.out.println("birth-fertility," + scape.getIteration() + "," + getAge() + "," + intProps[BEGIN_CHILD_BEARING_AGE] + "," + intProps[END_CHILD_BEARING_AGE] + "," + partner.getAge() + "," + partner.intProps[BEGIN_CHILD_BEARING_AGE] + "," + partner.intProps[END_CHILD_BEARING_AGE]);\n'
if args.reproduction == "specified":
    observer = """            if (getAge() < intProps[BEGIN_CHILD_BEARING_AGE] || getAge() > intProps[END_CHILD_BEARING_AGE] || partner.getAge() < partner.intProps[BEGIN_CHILD_BEARING_AGE] || partner.getAge() > partner.intProps[END_CHILD_BEARING_AGE]) throw new IllegalStateException("Fertility eligibility");
            if (floatProps[SUGAR_AMOUNT] <= 5 || partner.floatProps[SUGAR_AMOUNT] <= 5) throw new IllegalStateException("Sugar eligibility");
""" + observer
data = data.replace(marker, observer + marker)
modified = output / "SugarAgent.java"
modified.write_text(data, encoding="latin-1")
sources[sources.index(source)] = modified
classes = output / "classes"
classes.mkdir()
java = Path(manifest["command"][0])
library = reference / "reference/JAWAS/lib"
with (output / "compile.log").open("w") as log:
    subprocess.run([str(java.with_name("javac")), "-encoding", "ISO-8859-1", "-cp", str(library), "-d", str(classes), *map(str, sources)],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
adapter = Path(__file__).resolve().parent.parent / "buzing_2005/Replay.java"
assert hashlib.sha256(adapter.read_bytes()).hexdigest() == manifest["adapter_sha256"]
command = [str(java), "-Djava.awt.headless=true", f"-Dreplication.seed={args.seed}", "-cp", f"{classes}:{library}", str(adapter)]
provenance = {"study": "Buzing2003", "subcycles": args.subcycles, "reproduction": args.reproduction, "policy": args.policy, "threshold": args.threshold, "seed": args.seed, "cycles": 500,
              "reference_manifest": manifest, "overrides": overrides, "source_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "configuration_sha256": {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((output / "config").rglob("*.cfg"))},
              "command": command, "scope": "Specification reconstruction using newer recovered source; removal policy and historical fidelity unresolved."}
(output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
with (output / "run.log").open("w") as log:
    result = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, timeout=120)
(output / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
assert result.returncode == 0
series = {}
for path in (output / "data").glob("*.avg"):
    rows = [line.split() for line in path.read_text().splitlines()]
    assert [int(r[0]) for r in rows] == list(range(500))
    assert all(len(r) == 2 and math.isfinite(float(r[1])) for r in rows)
    series[path.name] = [float(r[1]) for r in rows]
assert len(series) == 7
population = series["experiment_0_.numberOfAgents.avg"]
assert all(n.is_integer() and n >= 0 for n in population)
assert all(listen == int(communicating) for listen, pop in zip(series["experiment_0_.listenPref.avg"], population) if pop > 0)
log = (output / "run.log").read_text()
assert f"iterations=500,initial=400,final={int(population[-1])}" in log
births = [list(map(float, line.split(',')[1:])) for line in log.splitlines() if line.startswith('birth2003,')]
assert all(0 <= r[0] < 500 and r[1] >= 0 and r[2] >= 0 for r in births)
fertility = [list(map(int, line.split(',')[1:])) for line in log.splitlines() if line.startswith('birth-fertility,')]
assert len(fertility) == len(births)
assert all(len(r) == 3 for r in births) and all(len(r) == 7 for r in fertility)
assert [r[0] for r in fertility] == [r[0] for r in births]
invalid_fertility = sum(not (r[2] <= r[1] <= r[3] and r[5] <= r[4] <= r[6]) for r in fertility)
invalid_sugar = sum(r[1] <= 5 or r[2] <= 5 for r in births)
if args.reproduction == "specified":
    assert invalid_fertility == invalid_sugar == 0
report = {"subcycles": args.subcycles, "reproduction": args.reproduction, "invalid_fertility_births": invalid_fertility, "not_above_sugar_threshold_births": invalid_sugar, "scalar_observations": 3500, "births": len(births), "initial_population": 400, "final_population": int(population[-1]),
          "fixed_listening_verified": True, "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((output / "data").iterdir())},
          "scope": "Operational specification reconstruction, not completed paper replication."}
(output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "output_sha256"}))
