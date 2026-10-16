"""Independently audit the fertility correction and compare every completed paired seed."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("ensemble", type=Path)
parser.add_argument("mode", choices=("prefix", "complete"))
parser.add_argument("output", type=Path)
parser.add_argument("--correction", choices=("own-range", "own-range-positive-sugar"), default="own-range")
args = parser.parse_args()
protocol = json.loads((args.ensemble / "protocol.json").read_text())
assert protocol["cycles"] == 2000 and protocol["runs"] == 150
for name, checksum in protocol["runner_sha256"].items():
    assert hashlib.sha256((args.ensemble / "runner" / name).read_bytes()).hexdigest() == checksum
expected = [f"{model}-ct{threshold}-seed{seed}" for model in ("paper-com0", "paper-com1", "paper-com2")
            for threshold in range(5) for seed in range(10)]
ledger_bytes = (args.ensemble / "completed.jsonl").read_bytes()
ledger = [json.loads(line) for line in ledger_bytes.splitlines()]
assert ledger and [r["name"] for r in ledger] == expected[:len(ledger)]
assert all(r["exit_code"] == 0 for r in ledger)
if args.mode == "complete":
    assert len(ledger) == 150
    assert json.loads((args.ensemble / "exit.json").read_text()) == {"exit_code": 0, "completed_runs": 150}
rows = []
for entry in ledger:
    run = args.ensemble / entry["name"]
    baseline = Path(protocol["baseline"]) / entry["name"]
    provenance = json.loads((run / "provenance.json").read_text())
    manifest = json.loads((baseline / "manifest.json").read_text())
    assert manifest["cycles"] == 2000 and manifest["unpaced"]
    assert entry["name"] == f"{manifest['variant']}-ct{manifest['threshold']}-seed{manifest['seed']}"
    assert provenance["mode"] == args.correction and provenance["baseline_manifest"] == manifest
    assert Path(provenance["baseline"]) == baseline
    assert json.loads((run / "exit.json").read_text()) == {"exit_code": 0}
    source = (run / "SugarAgent.java").read_bytes()
    assert hashlib.sha256(source).hexdigest() == provenance["observer_source_sha256"]
    restored = source.decode("latin-1")
    observer_lines = [line for line in restored.splitlines(keepends=True) if 'System.out.println("parent-eligibility,"' in line]
    assert len(observer_lines) == 1
    restored = restored.replace(observer_lines[0], "")
    for bound, operator in (("BEGIN_CHILD_BEARING_AGE", "<"), ("END_CHILD_BEARING_AGE", ">")):
        corrected = f"if (a.getAge() {operator} a.intProps[{bound}]) continue;"
        assert restored.count(corrected) == 1
        restored = restored.replace(corrected, f"if (a.getAge() {operator} intProps[{bound}]) continue;")
    if args.correction == "own-range-positive-sugar":
        wealth_lines = [line for line in restored.splitlines(keepends=True) if 'System.out.println("birth-wealth,"' in line]
        assert len(wealth_lines) == 1
        restored = restored.replace(wealth_lines[0], "")
        for corrected, original in (
            ("if (floatProps[SUGAR_AMOUNT] <= intProps[MIN_REPRODUCTION_SUGAR]) return;",
             "if (floatProps[SUGAR_AMOUNT] < intProps[MIN_REPRODUCTION_SUGAR]) return;"),
            ("if (a.floatProps[SUGAR_AMOUNT] <= a.intProps[MIN_REPRODUCTION_SUGAR]) continue;",
             "if (a.floatProps[SUGAR_AMOUNT] < a.intProps[MIN_REPRODUCTION_SUGAR]) continue;"),
        ):
            assert restored.count(corrected) == 1
            restored = restored.replace(corrected, original)
    original_source = next(Path(p) for p in manifest["source_sha256"] if Path(p).name == "SugarAgent.java")
    assert restored == original_source.read_text(encoding="latin-1")
    for name, checksum in manifest["source_sha256"].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
    for name, checksum in manifest["configuration_sha256"].items():
        assert hashlib.sha256((baseline / name).read_bytes()).hexdigest() == checksum
        assert (run / name).read_bytes() == (baseline / name).read_bytes()
    native_audit = json.loads((run / "audit.json").read_text())
    summaries = {}
    for label, path, checksums in (("baseline", baseline, manifest["output_sha256"]),
                                    ("corrected", run, native_audit["output_sha256"])):
        series = {}
        for name, checksum in checksums.items():
            raw = (path / name).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == checksum
            if name.endswith(".avg"):
                values = [line.split() for line in raw.decode().splitlines()]
                assert [int(row[0]) for row in values] == list(range(2000))
                assert all(len(row) == 2 and math.isfinite(float(row[1])) for row in values)
                series[Path(name).name] = [float(row[1]) for row in values]
        assert len(series) == 7
        pop = series["experiment_0_.numberOfAgents.avg"]
        assert all(n.is_integer() and n >= 0 for n in pop)
        extinct = next((i for i, n in enumerate(pop) if n == 0), None)
        if extinct is not None:
            assert all(n == 0 for n in pop[extinct:])
        alive = [i for i in range(1500, 2000) if pop[i] > 0]
        summary = {"final_population": pop[-1], "extinction_cycle": extinct + 1 if extinct is not None else None,
                   "late_population": statistics.mean(pop[1500:])}
        for gene in ("talk", "listen"):
            values = series[f"experiment_0_.{gene}Pref.avg"]
            assert all(0 <= n <= 1 for n in values)
            summary[f"late_{gene}"] = statistics.mean(values[i] for i in alive) if alive else None
        summaries[label] = summary
    log = (run / "run.log").read_text()
    births = [list(map(int, line.split(",")[1:])) for line in log.splitlines() if line.startswith("parent-eligibility,")]
    assert len(births) == native_audit["observed_births"]
    assert all(0 <= r[0] < 2000 and r[2] <= r[1] <= r[3] and r[5] <= r[4] <= r[6] for r in births)
    compressed_births = gzip.decompress((run / "births.csv.gz").read_bytes()).decode().splitlines()
    assert [list(map(int, line.split(','))) for line in compressed_births[1:]] == births
    if args.correction == "own-range-positive-sugar":
        wealth = [list(map(float, line.split(',')[1:])) for line in log.splitlines() if line.startswith('birth-wealth,')]
        assert len(wealth) == len(births)
        assert all(r[1] > r[3] and r[2] > r[4] and r[3] == r[4] == 0 for r in wealth)
        wealth_csv = gzip.decompress((run / "wealth.csv.gz").read_bytes()).decode().splitlines()
        assert [list(map(float, line.split(','))) for line in wealth_csv[1:]] == wealth
    counts = [list(map(int, line.split(',')[1:])) for line in log.splitlines() if line.startswith('harvest-counts,')]
    assert [r[0] for r in counts] == list(range(2000))
    assert all(0 <= shared <= meals <= consumers and 2 * shared <= shared_consumers <= consumers
               and meals - shared == consumers - shared_consumers for _, meals, shared, consumers, shared_consumers in counts)
    rows.append({"name": entry["name"], "protocol": manifest["variant"], "threshold": manifest["threshold"],
                 "seed": manifest["seed"], "births": len(births), "log_sha256": hashlib.sha256((run / "run.log").read_bytes()).hexdigest(),
                 "corrected_output_sha256": native_audit["output_sha256"], **summaries})
groups = []
for model in ("paper-com0", "paper-com1", "paper-com2"):
    for threshold in range(5):
        group = [r for r in rows if r["protocol"] == model and r["threshold"] == threshold]
        if not group:
            continue
        summary = {"protocol": model, "threshold": threshold, "paired_seeds": len(group)}
        for label in ("baseline", "corrected"):
            summary[label] = {"surviving_seeds": sum(r[label]["final_population"] > 0 for r in group),
                              "late_mean_population": statistics.mean(r[label]["late_population"] for r in group)}
        summary["changed_survival_seeds"] = [r["seed"] for r in group if (r['baseline']['final_population'] > 0) != (r['corrected']['final_population'] > 0)]
        groups.append(summary)
report = {"mode": args.mode, "correction": args.correction, "complete": args.mode == "complete", "paired_runs": len(rows),
          "scalar_observations_both_conditions": len(rows) * 28000, "corrected_births": sum(r["births"] for r in rows),
          "invalid_parent_births": 0, "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(), "groups": groups, "runs": rows,
          "scope": "Paired specification correction; not independent additional seeds, not a historical-source or paper-level replication verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("groups", "runs")}))
