"""Independently audit completed native runs and preserve a prefix or full snapshot."""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("mode", choices=["prefix", "complete"])
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol_bytes = (args.run / "protocol.json").read_bytes()
protocol = json.loads(protocol_bytes)
assert protocol["protocols"] == ["paper-com0", "paper-com1", "paper-com2"]
assert protocol["thresholds"] == list(range(5)) and protocol["seeds"] == list(range(10))
assert protocol["cycles"] == 2000 and protocol["runs"] == 150
for name, checksum in protocol["runner_sha256"].items():
    assert hashlib.sha256((args.run / "runner" / name).read_bytes()).hexdigest() == checksum
ledger_bytes = (args.run / "completed.jsonl").read_bytes()
assert ledger_bytes.endswith(b"\n"), "Retry after the ledger writer flushes"
ledger = [json.loads(line) for line in ledger_bytes.splitlines()]
expected = [(model, threshold, seed) for model in protocol["protocols"] for threshold in range(5) for seed in range(10)]
assert 0 < len(ledger) <= len(expected)
if args.mode == "complete":
    assert len(ledger) == 150
    assert json.loads((args.run / "exit.json").read_text()) == {"exit_code": 0, "completed_runs": 150}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "protocol.json").write_bytes(protocol_bytes)
(args.output / "completed.jsonl").write_bytes(ledger_bytes)
summary = []
for record, (model, threshold, seed) in zip(ledger, expected):
    name = f"{model}-ct{threshold}-seed{seed}"
    assert record["name"] == name and record["exit_code"] == 0
    run = args.run / name
    manifest_bytes = (run / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert (manifest["variant"], manifest["threshold"], manifest["seed"], manifest["cycles"]) == (model, threshold, seed, 2000)
    for path, checksum in manifest["source_sha256"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == checksum
    for path, checksum in manifest["configuration_sha256"].items():
        assert hashlib.sha256((run / path).read_bytes()).hexdigest() == checksum
    settings = {}
    for config in (run / "config").rglob("*.cfg"):
        for line in config.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                key, value = line.split("=", 1)
                settings[key.strip()] = value.strip()
    for key, expected_value in {"randomSeed": seed, "maxSugarHarvest": threshold, "runLength": 2000,
                                "numberOfRuns": 1, "nrOfSubcycles": 1, "sugarRichness": 1,
                                "minInitialSugar": 0, "maxReproductionSugar": 0,
                                "mutationSigma": 0.1, "message.removeAfterNIterations": 0}.items():
        assert float(settings[key].removesuffix("f")) == expected_value, key
    for key, expected_value in {"message.removeAfterListening": model == "paper-com1",
                                "message.removeAfterResponse": model == "paper-com2",
                                "mutationOperator.listenPref": model != "paper-com0",
                                "mutationOperator.talkPref": model != "paper-com0"}.items():
        assert settings[key] == str(expected_value).lower(), key
    if model == "paper-com0":
        assert all(float(settings[key]) == 0 for key in ("minListenPref", "maxListenPref", "minTalkPref", "maxTalkPref"))
    assert manifest["adapter_sha256"] == protocol["runner_sha256"]["Replay.java"]
    scalar = {}
    dest = args.output / name
    dest.mkdir()
    (dest / "manifest.json").write_bytes(manifest_bytes)
    for relative, checksum in manifest["output_sha256"].items():
        data = (run / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == checksum
        (dest / (Path(relative).name + ".gz")).write_bytes(gzip.compress(data, mtime=0))
        if relative.endswith(".avg") or relative.endswith(".sum"):
            rows = [line.split() for line in data.decode().splitlines()]
            assert len(rows) == 2000 and all(len(row) == 2 for row in rows)
            assert [int(row[0]) for row in rows] == list(range(2000))
            values = [float(row[1]) for row in rows]
            assert all(math.isfinite(value) and value >= 0 for value in values)
            scalar[Path(relative).name.removeprefix("experiment_0_.")] = values
    assert len(scalar) == 8
    population = scalar["numberOfAgents.avg"]
    assert all(value.is_integer() for value in population)
    zero = [index for index, value in enumerate(population) if value == 0]
    if zero:
        assert all(value == 0 for value in population[zero[0]:])
    for metric in ("talkPref.avg", "listenPref.avg", "cooperating.avg"):
        assert all(0 <= value <= 1 for value in scalar[metric])
    if model == "paper-com0":
        assert not any(scalar["talkPref.avg"]) and not any(scalar["listenPref.avg"])
    log = (run / "run.log").read_bytes()
    assert f"iterations=2000,initial=1000,final={int(population[-1])}" in log.decode()
    assert manifest["final_population"] == population[-1] and manifest["scalar_observations"] == 14000
    counts = [list(map(int, line.split(',')[1:])) for line in log.decode().splitlines() if line.startswith("harvest-counts,")]
    assert len(counts) == 2000 and [row[0] for row in counts] == list(range(2000))
    (dest / "run.log.gz").write_bytes(gzip.compress(log, mtime=0))
    undefined = 0
    with (dest / "cooperation.csv").open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["record", "cycle", "harvest_events", "shared_events", "consumer_participations", "shared_participations", "shared_event_fraction", "shared_participation_fraction"])
        for index, meals, shared, consumers, shared_consumers in counts:
            assert 0 <= shared <= meals <= consumers and 2 * shared <= shared_consumers <= consumers
            assert meals - shared == consumers - shared_consumers
            assert (meals == 0) == (consumers == 0)
            undefined += meals == 0
            writer.writerow([index, index + 1, meals, shared, consumers, shared_consumers,
                             shared / meals if meals else None, shared_consumers / consumers if consumers else None])
    alive_late = [index for index in range(1500, 2000) if population[index] > 0]
    summary.append({"name": name, "protocol": model, "threshold": threshold, "seed": seed,
                    "final_population": int(population[-1]), "extinction_cycle": zero[0] + 1 if zero else None,
                    "mean_population_cycles_1501_2000": statistics.mean(population[1500:]),
                    "mean_talk_alive_cycles_1501_2000": statistics.mean(scalar["talkPref.avg"][i] for i in alive_late) if alive_late else None,
                    "mean_listen_alive_cycles_1501_2000": statistics.mean(scalar["listenPref.avg"][i] for i in alive_late) if alive_late else None,
                    "undefined_cooperation_cycles": undefined, "log_sha256": hashlib.sha256(log).hexdigest()})
report = {"mode": args.mode, "complete_ensemble": args.mode == "complete", "validated_runs": len(summary),
          "required_runs": 150, "scalar_observations": 14000 * len(summary), "harvest_count_rows": 2000 * len(summary),
          "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(), "runs": summary,
          "scope": "Native reconstruction validation; no historical source-equivalence or scientific replication verdict. Late window is descriptive, not a fitted acceptance criterion."}
(args.output / "audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "runs"}))
