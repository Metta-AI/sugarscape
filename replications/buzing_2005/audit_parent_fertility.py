"""Replay a frozen native run while observing or correcting partner fertility bounds."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("baseline", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("mode", choices=("observe", "own-range"))
parser.add_argument("--observe-wealth", action="store_true")
args = parser.parse_args()
baseline = args.baseline.resolve()
manifest = json.loads((baseline / "manifest.json").read_text())
assert manifest["variant"] in ("paper-com0", "paper-com1", "paper-com2")
assert manifest["cycles"] == 2000 and manifest["unpaced"]
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
for name, checksum in manifest["configuration_sha256"].items():
    assert hashlib.sha256((baseline / name).read_bytes()).hexdigest() == checksum
for name, checksum in manifest["output_sha256"].items():
    assert hashlib.sha256((baseline / name).read_bytes()).hexdigest() == checksum
adapter = Path(__file__).with_name("Replay.java").resolve()
assert hashlib.sha256(adapter.read_bytes()).hexdigest() == manifest["adapter_sha256"]
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
shutil.copytree(baseline / "config", output / "config")
classes = output / "classes"
classes.mkdir()
sources = [Path(name) for name in manifest["source_sha256"]]
source = next(p for p in sources if p.name == "SugarAgent.java")
data = source.read_text(encoding="latin-1")
if args.mode == "own-range":
    for bound, operator in (("BEGIN_CHILD_BEARING_AGE", "<"), ("END_CHILD_BEARING_AGE", ">")):
        old = f"if (a.getAge() {operator} intProps[{bound}]) continue;"
        assert data.count(old) == 1
        data = data.replace(old, f"if (a.getAge() {operator} a.intProps[{bound}]) continue;")
marker = '            child = new SugarAgent("SugarAgentChild", childProps);'
assert data.count(marker) == 1
insertion = '''            System.out.println("parent-eligibility," + scape.getIteration() + "," + getAge() + "," + intProps[BEGIN_CHILD_BEARING_AGE] + "," + intProps[END_CHILD_BEARING_AGE] + "," + partner.getAge() + "," + partner.intProps[BEGIN_CHILD_BEARING_AGE] + "," + partner.intProps[END_CHILD_BEARING_AGE]);
'''
if args.observe_wealth:
    wealth_marker = "            floatProps[SUGAR_AMOUNT] /= 2.0f;"
    assert data.count(wealth_marker) == 1
    wealth_observer = '            System.out.println("birth-wealth," + scape.getIteration() + "," + floatProps[SUGAR_AMOUNT] + "," + partner.floatProps[SUGAR_AMOUNT] + "," + intProps[MIN_REPRODUCTION_SUGAR] + "," + partner.intProps[MIN_REPRODUCTION_SUGAR]);\n'
    data = data.replace(wealth_marker, wealth_observer + wealth_marker)
observed_source = output / "SugarAgent.java"
observed_source.write_text(data.replace(marker, insertion + marker), encoding="latin-1")
sources[sources.index(source)] = observed_source
java = Path(manifest["command"][0])
library = baseline / "reference/JAWAS/lib"
with (output / "compile.log").open("w") as log:
    subprocess.run([str(java.with_name("javac")), "-encoding", "ISO-8859-1", "-cp", str(library),
                    "-d", str(classes), *map(str, sources)], stdout=log, stderr=subprocess.STDOUT, check=True)
command = [str(java), "-Djava.awt.headless=true", f"-Dreplication.seed={manifest['seed']}",
           "-cp", f"{classes}:{library}", str(adapter)]
provenance = {"mode": args.mode, "observe_wealth": args.observe_wealth, "baseline": str(baseline), "baseline_manifest": manifest,
              "observer_source_sha256": hashlib.sha256(observed_source.read_bytes()).hexdigest(),
              "command": command, "scope": "Own-range correction is specification-based, not recovered historical code. No other rule changed."}
(output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
with (output / "run.log").open("w") as log:
    process = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, timeout=120)
(output / "exit.json").write_text(json.dumps({"exit_code": process.returncode}) + "\n")
assert process.returncode == 0
rows = [list(map(int, line.split(",")[1:])) for line in (output / "run.log").read_text().splitlines()
        if line.startswith("parent-eligibility,")]
assert rows
invalid = [r for r in rows if not r[5] <= r[4] <= r[6]]
assert all(r[2] <= r[1] <= r[3] for r in rows)
if args.mode == "own-range":
    assert not invalid
checksums = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((output / "data").iterdir())}
assert checksums.keys() == manifest["output_sha256"].keys()
matching = sum(checksum == manifest["output_sha256"][name] for name, checksum in checksums.items())
if args.mode == "observe":
    assert matching == 10
scalar_observations = 0
for path in sorted((output / "data").glob("*.avg")):
    values = [line.split() for line in path.read_text().splitlines()]
    assert [int(row[0]) for row in values] == list(range(2000))
    assert all(len(row) == 2 and math.isfinite(float(row[1])) for row in values)
    scalar_observations += len(values)
assert scalar_observations == 14000
population = [line.split() for line in (output / "data/experiment_0_.numberOfAgents.avg").read_text().splitlines()]
assert all(float(row[1]).is_integer() and float(row[1]) >= 0 for row in population)
assert f"iterations=2000,initial=1000,final={int(float(population[-1][1]))}" in (output / "run.log").read_text()
with gzip.open(output / "births.csv.gz", "wt") as stream:
    stream.write("cycle,self_age,self_begin,self_end,partner_age,partner_begin,partner_end\n")
    for row in rows:
        stream.write(",".join(map(str, row)) + "\n")
report = {"mode": args.mode, "cycles": 2000, "scalar_observations": scalar_observations, "observed_births": len(rows), "partner_outside_own_range": len(invalid),
          "partner_below_own_minimum": sum(r[4] < r[5] for r in rows), "partner_above_own_maximum": sum(r[4] > r[6] for r in rows),
          "matching_baseline_files": matching, "final_population": float(population[-1][1]), "output_sha256": checksums,
          "scope": "Native rule audit; no paper-level replication verdict."}
if args.observe_wealth:
    wealth = [list(map(float, line.split(",")[1:])) for line in (output / "run.log").read_text().splitlines()
              if line.startswith("birth-wealth,")]
    assert len(wealth) == len(rows) and all(r[3] == r[4] == 0 for r in wealth)
    report["wealth_before_halving"] = {"either_parent_zero": sum(r[1] == 0 or r[2] == 0 for r in wealth),
                                      "both_parents_zero": sum(r[1] == r[2] == 0 for r in wealth),
                                      "initiator_zero": sum(r[1] == 0 for r in wealth),
                                      "partner_zero": sum(r[2] == 0 for r in wealth)}
    with gzip.open(output / "wealth.csv.gz", "wt") as stream:
        stream.write("cycle,initiator_sugar,partner_sugar,initiator_threshold,partner_threshold\n")
        for row in wealth:
            stream.write(",".join(map(str, row)) + "\n")
(output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "output_sha256"}))
