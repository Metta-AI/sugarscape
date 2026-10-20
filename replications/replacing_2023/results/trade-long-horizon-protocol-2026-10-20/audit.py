"""Audit complete native horizon extensions and their original archived prefixes."""
from pathlib import Path
import gzip
import hashlib
import json
import math
import statistics

root = Path(__file__).resolve().parent
base = root.parent.parent
engine = base / "sugarscape-dtl-replacing-reference"
prior = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15"
protocol_raw = (root / "protocol.json").read_bytes()
p = json.loads(protocol_raw)
m = json.loads((root / "manifest.json").read_bytes())
assert hashlib.sha256(protocol_raw).hexdigest() == m["protocol_sha256"]
terminal = json.loads((root / "terminal.json").read_bytes())
assert terminal["exit_code"] == 0 and terminal["runs"] == 3
assert all(hashlib.sha256((engine / f).read_bytes()).hexdigest() == digest for f, digest in m["source_sha256"].items())
conditions = [p["baseline"], *[t["treatment"] for t in p["treatments"]]]
completed = json.loads((root / "completed.json").read_bytes())
assert [(r["seed"], r["condition"]) for r in completed] == [(s, c) for s in p["pilot_seeds"] for c in conditions]
originals = {p["baseline"]: p["baseline_sha256"], **{t["treatment"]: t["configuration_sha256"] for t in p["treatments"]}}
measurements = []
for record in completed:
    seed, name = record["seed"], record["condition"]
    run = root / f"seed-{seed}" / name
    original = (engine / "examples" / (name + ".json")).read_bytes()
    assert hashlib.sha256(original).hexdigest() == originals[name]
    expected = json.loads(original)
    expected.update(seed=seed, timesteps=10000, headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
    assert json.loads((run / "config.json").read_bytes()) == expected
    assert expected["agentReplacements"] == 0
    assert json.loads((run / "exit.json").read_bytes())["exit_code"] == 0
    raw = (run / "trajectory.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
    rows = json.loads(raw)
    prefix = json.loads(gzip.decompress((prior / f"seed-{seed}" / name / "trajectory.json.gz").read_bytes()))
    assert rows[:len(prefix)] == prefix
    assert len(rows) == record["observations"] <= 10001
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    assert rows[0]["population"] == expected["startingAgents"]
    assert all(r["seed"] == seed and math.isfinite(r["population"]) and int(r["population"]) == r["population"] and 0 <= r["population"] <= 2500 for r in rows)
    assert len(rows) == 10001 or rows[-1]["population"] == 0
    zeros = [r["timestep"] for r in rows if r["population"] == 0]
    assert not zeros or all(r["population"] == 0 for r in rows[zeros[0]:])
    population = [r["population"] for r in rows] + [0] * (10001 - len(rows))
    blocks = [statistics.mean(population[start:start + 1000]) for start in range(1, 10001, 1000)]
    measurements.append({**record, "original_prefix_all_fields_exact": True, "absorbing_zero_extension_steps": 10001 - len(rows), "extinction_steps": zeros[:1], "consecutive_1000_step_means": blocks, "mean_steps_5001_10000": statistics.mean(population[5001:10001]), "last_block_minus_previous": blocks[-1] - blocks[-2], "last_five_blocks_range": max(blocks[5:]) - min(blocks[5:])})
paired = []
for seed in p["pilot_seeds"]:
    controls = {r["condition"]: r for r in measurements if r["seed"] == seed}
    baseline = controls[p["baseline"]]["mean_steps_5001_10000"]
    for condition in conditions[1:]:
        delta = controls[condition]["mean_steps_5001_10000"] - baseline
        comparison = {"seed": seed, "condition": condition, "absolute_change": delta, "relative_change_status": "undefined_zero_baseline"}
        if baseline != 0:
            comparison.update(relative_change_status="defined", relative_change=delta / baseline)
        paired.append(comparison)
result = {"protocol_sha256": m["protocol_sha256"], "runs": len(measurements), "observations": sum(r["observations"] for r in measurements), "measurements": measurements, "paired": paired, "scope": "Single-seed qualification, not twenty-seed inference or carrying-capacity proof. All windows fixed before execution; remaining drift reported without a fitted acceptance threshold."}
(root / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
print(json.dumps(result, indent=2, allow_nan=False))
