"""Compare a completely audited reconstruction ensemble with published claims."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("audit", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
audit_bytes = (args.audit / "audit.json").read_bytes()
audit = json.loads(audit_bytes)
assert audit["complete_ensemble"] and audit["mode"] == "complete"
assert audit["validated_runs"] == 150 and len(audit["runs"]) == 150
assert audit["scalar_observations"] == 2100000
expected = {(model, threshold, seed) for model in ("paper-com0", "paper-com1", "paper-com2") for threshold in range(5) for seed in range(10)}
assert {(r["protocol"], r["threshold"], r["seed"]) for r in audit["runs"]} == expected
# Descriptive levels in sections5.5–5.7 are approximate, not published confidence bounds.
approximate = {
    ("paper-com1", 1): {"talk": 0.8, "listen": 0.85},
    ("paper-com1", 2): {"population": 800, "listen": 0.8},
    ("paper-com1", 3): {"population": 1000, "talk": 0.45, "listen": 0.75},
    ("paper-com1", 4): {"population": 1000, "listen": 0.65},
}
rows = []
for model in ("paper-com0", "paper-com1", "paper-com2"):
    for threshold in range(5):
        runs = [r for r in audit["runs"] if r["protocol"] == model and r["threshold"] == threshold]
        assert sorted(r["seed"] for r in runs) == list(range(10))
        late_population, late_talk, late_listen = [], [], []
        shared_events, events, shared_consumers, consumers = 0, 0, 0, 0
        for run in runs:
            path = args.audit / run["name"]
            manifest = json.loads((path / "manifest.json").read_text())
            series = {}
            for relative, checksum in manifest["output_sha256"].items():
                data = gzip.decompress((path / (Path(relative).name + ".gz")).read_bytes())
                assert hashlib.sha256(data).hexdigest() == checksum
                if relative.endswith(".avg"):
                    series[Path(relative).name.removeprefix("experiment_0_.")] = [float(line.split()[1]) for line in data.decode().splitlines()]
            population = series["numberOfAgents.avg"]
            assert len(population) == 2000 and population[-1] == run["final_population"]
            late_population.append(statistics.mean(population[1500:]))
            alive = [i for i in range(1500, 2000) if population[i] > 0]
            if alive:
                late_talk.append(statistics.mean(series["talkPref.avg"][i] for i in alive))
                late_listen.append(statistics.mean(series["listenPref.avg"][i] for i in alive))
            log = gzip.decompress((path / "run.log.gz").read_bytes())
            assert hashlib.sha256(log).hexdigest() == run["log_sha256"]
            for line in log.decode().splitlines():
                if line.startswith("harvest-counts,"):
                    index, count, shared, participants, shared_participants = map(int, line.split(',')[1:])
                    if index >= 1500:
                        events += count
                        shared_events += shared
                        consumers += participants
                        shared_consumers += shared_participants
        expected_survival = threshold == 4 if model == "paper-com0" else threshold > 0
        matched = sum((r["final_population"] > 0) == expected_survival for r in runs)
        observed = {"population": statistics.mean(late_population),
                    "talk": statistics.mean(late_talk) if late_talk else None,
                    "listen": statistics.mean(late_listen) if late_listen else None}
        levels = approximate.get((model, threshold), {})
        rows.append({"protocol": model, "threshold": threshold, "seeds": 10,
                     "expected_survival": expected_survival, "matching_survival_seeds": matched,
                     "surviving_seeds": sum(r["final_population"] > 0 for r in runs),
                     "extinction_cycles": [r["extinction_cycle"] for r in runs],
                     "late_alive_seed_count": len(late_talk), "late_mean_across_seeds": observed,
                     "published_approximate_levels": levels,
                     "observed_minus_published_approximate": {key: observed[key] - value if observed[key] is not None else None for key, value in levels.items()},
                     "late_pooled_shared_event_fraction": shared_events / events if events else None,
                     "late_pooled_shared_participation_fraction": shared_consumers / consumers if consumers else None})
report = {"source": "https://www.jasss.org/8/1/2.html", "sections": ["4.8", "5.2", "5.3", "5.5", "5.7", "5.11"],
          "audit_sha256": hashlib.sha256(audit_bytes).hexdigest(), "groups": rows,
          "interpretation": "Literal reported survival pattern compared across ten new seeds per condition. Approximate paper levels receive descriptive differences, not invented equivalence margins. Unknown publication seeds, historical source, and reproductive-rule fidelity prevent an automatic paper verdict.",
          "measurement": "Late cycles1501–2000. Population averages include extinction zeros. Gene means use alive cycles and report contributing seed count. Cooperation ratios pool event counts, not independent samples."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
with (args.output / "survival.csv").open("w") as stream:
    fields = ["protocol", "threshold", "seeds", "expected_survival", "matching_survival_seeds", "surviving_seeds"]
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows({key: row[key] for key in fields} for row in rows)
print(json.dumps({"groups": len(rows), "runs": 150, "automatic_paper_verdict": False}))
