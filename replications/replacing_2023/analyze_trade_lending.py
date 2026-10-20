"""Independently validate and summarize all sixty paired native trajectories."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
batch = args.batch.resolve()
protocol_bytes = (batch / "protocol.json").read_bytes()
protocol = json.loads(protocol_bytes)
manifest = json.loads((batch / "manifest.json").read_text())
assert hashlib.sha256(protocol_bytes).hexdigest() == manifest["protocol_sha256"]
assert protocol_bytes == Path(__file__).with_name("trade-lending-protocol.json").read_bytes()
engine = Path(manifest["engine"])
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
conditions = [protocol["baseline"], *[t["treatment"] for t in protocol["treatments"]]]
checksums = [protocol["baseline_sha256"], *[t["configuration_sha256"] for t in protocol["treatments"]]]
originals = {}
for name, checksum in zip(conditions, checksums, strict=True):
    raw = (engine / "examples" / f"{name}.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == checksum
    originals[name] = json.loads(raw)
completed = [json.loads(line) for line in (batch / "completed.jsonl").read_text().splitlines()]
assert [(r["seed"], r["condition"]) for r in completed] == [(seed, name) for seed in protocol["seeds"] for name in conditions]
assert len(completed) == 60
measurements = {}
for record in completed:
    assert record["exit_code"] == 0
    seed, name = record["seed"], record["condition"]
    run = batch / f"seed-{seed}" / name
    config_bytes = (run / "config.json").read_bytes()
    assert hashlib.sha256(config_bytes).hexdigest() == record["config_sha256"]
    expected = dict(originals[name])
    expected.update(seed=seed, headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
    assert json.loads(config_bytes) == expected
    assert expected["agentReplacements"] == 0
    raw = (run / "trajectory.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
    rows = json.loads(raw)
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    assert rows[0]["population"] == expected["startingAgents"]
    assert all(r["seed"] == seed and math.isfinite(r["population"]) and
               int(r["population"]) == r["population"] and 0 <= r["population"] <= 2500 for r in rows)
    horizon = protocol["horizon"]
    assert len(rows) <= horizon + 1
    assert len(rows) == horizon + 1 or rows[-1]["population"] == 0
    zeros = [r["timestep"] for r in rows if r["population"] == 0]
    assert not zeros or all(r["population"] == 0 for r in rows[zeros[0]:])
    population = [r["population"] for r in rows] + [0] * (horizon + 1 - len(rows))
    early = statistics.mean(population[1:protocol["window_start_inclusive"]])
    late = statistics.mean(population[protocol["window_start_inclusive"]:protocol["window_stop_inclusive"] + 1])
    measurements[seed, name] = {"seed": seed, "condition": name, "native_observations": len(rows),
        "extinction_step": zeros[0] if zeros else None, "absorbing_zero_extension_steps": horizon + 1 - len(rows),
        "terminal_population": population[-1], "early_mean": early, "late_mean": late,
        "late_minus_early": late - early, "trajectory_sha256": record["trajectory_sha256"]}
paired = []
for seed in protocol["seeds"]:
    baseline = measurements[seed, protocol["baseline"]]["late_mean"]
    for name in conditions[1:]:
        change = measurements[seed, name]["late_mean"] - baseline
        paired.append({"seed": seed, "condition": name, "late_mean_absolute_change": change,
                       "late_mean_relative_change": change / baseline if baseline != 0 else None,
                       "relative_change_status": "defined" if baseline != 0 else "undefined_zero_baseline"})
summaries = []
for name in conditions[1:]:
    pairs = [r for r in paired if r["condition"] == name]
    relative = [r["late_mean_relative_change"] for r in pairs]
    defined = all(value is not None for value in relative)
    summaries.append({"condition": name, "pairs": len(pairs),
        "mean_absolute_change": statistics.mean(r["late_mean_absolute_change"] for r in pairs),
        "undefined_relative_pairs": sum(value is None for value in relative),
        "mean_relative_change": statistics.mean(relative) if defined else None,
        "maximum_relative_change": max(relative) if defined else None})
report = {"status": "Paired diagnostic; historical paper protocol unresolved",
          "protocol_sha256": manifest["protocol_sha256"], "runs": len(completed),
          "measurements": list(measurements.values()), "paired": paired, "summaries": summaries,
          "interpretation": protocol["interpretation"]}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"runs": len(completed), "summaries": summaries}, indent=2))
