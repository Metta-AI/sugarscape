"""Audit all sixty extended trajectories and summarize fixed prospective windows."""
from pathlib import Path
import gzip
import hashlib
import json
import math
import statistics

root = Path(__file__).resolve().parent
base = root.parent.parent
p = json.loads((root / "protocol.json").read_bytes())
t = json.loads((root / "terminal.json").read_bytes())
assert t["all_requests_complete"] and t["completed"] == 35 and t["remaining"] == []
qualification = root.parent / "replacing-trade-passive-qualification-001"
q = json.loads((qualification / "audit.json").read_bytes())
assert all(q[k] == v for k, v in p["qualification_required"].items())
inventory = json.loads((root / "inventory.json").read_bytes())
assert hashlib.sha256((root / "inventory.json").read_bytes()).hexdigest() == p["recovery_inventory_sha256"]
completed = inventory["completed"] + json.loads((root / "completed.json").read_bytes())
lookup = {(r["seed"], r["condition"]): r for r in completed}
assert len(lookup) == len(completed) == 60
conditions = [p["baseline"], *[t["treatment"] for t in p["treatments"]]]
expected = {(seed, name) for seed in p["seeds"] for name in conditions}
assert set(lookup) == expected
native_manifest = json.loads((qualification / "manifest.json").read_bytes())
engine = base / "sugarscape-dtl-replacing-reference"
assert all(hashlib.sha256((engine / f).read_bytes()).hexdigest() == digest for f, digest in native_manifest["source_sha256"].items())
measurements = {}
for seed in p["seeds"]:
    for name in conditions:
        is_qualification = (seed, name) == (14133, "spice_growback")
        run = Path(lookup[seed, name]["directory"])
        assert json.loads((run / "exit.json").read_bytes())["exit_code"] == 0
        manifest = json.loads((run / "manifest.json").read_bytes())
        assert manifest["source_sha256"] == native_manifest["source_sha256"]
        assert manifest["python"] == native_manifest["python"]
        effective = json.loads((run / "effective-config.json").read_bytes())
        assert effective["timesteps"] == 10000 and effective["seed"] == seed
        assert effective["agentReplacements"] == 0
        prior = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15" / f"seed-{seed}" / name
        original = json.loads(gzip.decompress((prior / "config.json.gz").read_bytes()))
        assert all(effective[k] == v for k, v in original.items() if k not in ("timesteps", "logfile", "__README__"))
        prefix = [json.loads(line) for line in (run / "original-schedule.jsonl").read_text().splitlines()]
        assert prefix == json.loads(gzip.decompress((prior / "trajectory.json.gz").read_bytes()))
        raw = (run / "trajectory.json").read_bytes()
        expected_hash = q["native_trajectory_sha256"] if is_qualification else lookup[seed, name]["trajectory_sha256"]
        assert hashlib.sha256(raw).hexdigest() == expected_hash
        rows = json.loads(raw)
        assert [r["timestep"] for r in rows] == list(range(len(rows)))
        assert rows[0]["population"] == original["startingAgents"]
        assert len(rows) == 10001 or rows[-1]["population"] == 0
        assert len(rows) <= 10001
        for record in rows:
            assert record["seed"] == seed and 0 <= record["population"] <= 2500 and int(record["population"]) == record["population"]
            assert all(math.isfinite(x) for value in record.values() for x in (value if isinstance(value, list) else [value]))
        zeros = [r["timestep"] for r in rows if r["population"] == 0]
        assert not zeros or all(r["population"] == 0 for r in rows[zeros[0]:])
        population = [r["population"] for r in rows] + [0] * (10001 - len(rows))
        blocks = [statistics.mean(population[start:start + 1000]) for start in range(1, 10001, 1000)]
        measurements[seed, name] = {"seed": seed, "condition": name, "native_observations": len(rows), "original_schedule_records_exact": len(prefix), "trajectory_sha256": expected_hash, "extinction_steps": zeros[:1], "absorbing_zero_extension_steps": 10001 - len(rows), "consecutive_1000_step_means": blocks, "mean_steps_5001_10000": statistics.mean(population[5001:10001]), "last_block_minus_previous": blocks[-1] - blocks[-2], "last_five_blocks_range": max(blocks[5:]) - min(blocks[5:])}
paired = []
for seed in p["seeds"]:
    baseline = measurements[seed, p["baseline"]]["mean_steps_5001_10000"]
    for name in conditions[1:]:
        delta = measurements[seed, name]["mean_steps_5001_10000"] - baseline
        row = {"seed": seed, "condition": name, "absolute_change": delta, "relative_status": "undefined_zero_baseline"}
        if baseline != 0:
            row.update(relative_status="defined", relative_change=delta / baseline)
        paired.append(row)
summaries = []
for name in conditions[1:]:
    rows = [r for r in paired if r["condition"] == name]
    summary = {"condition": name, "pairs": len(rows), "mean_absolute_change": statistics.mean(r["absolute_change"] for r in rows), "undefined_relative_pairs": sum(r["relative_status"] != "defined" for r in rows)}
    if summary["undefined_relative_pairs"] == 0:
        summary.update(mean_relative_change=statistics.mean(r["relative_change"] for r in rows), maximum_relative_change=max(r["relative_change"] for r in rows), minimum_relative_change=min(r["relative_change"] for r in rows))
    summaries.append(summary)
report = {"inputs": len(measurements), "observations": sum(r["native_observations"] for r in measurements.values()), "measurements": list(measurements.values()), "paired": paired, "summaries": summaries, "scope": "Prospective horizon sensitivity using the unchanged released model and original20seed diagnostic. Historical seeds/window remain unknown; no stationary carrying-capacity or paper-completion claim."}
(root / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("measurements", "paired")}, indent=2))
