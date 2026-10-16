"""Audit all released examples without interpreting execution as replication."""
import argparse
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
batch = args.batch.resolve()
manifest = json.loads((batch / "manifest.json").read_text())
targets = json.loads(Path(__file__).with_name("published_targets.json").read_text())["table4"]
assert manifest["targets"] == targets
engine = Path(manifest["engine"])
for name, checksum in manifest["source_sha256"].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == checksum
completed = [json.loads(line) for line in (batch / "completed.jsonl").read_text().splitlines()]
assert len(completed) == len(targets) == 17
report = []
for record, target in zip(completed, targets, strict=True):
    name = target["configuration"]
    assert record["configuration"] == name and record["exit_code"] == 0
    original_bytes = (engine / "examples" / name).read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == target["released_config_sha256"]
    expected = json.loads(original_bytes)
    run = batch / Path(name).stem
    expected.update(headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
    assert json.loads((run / "config.json").read_text()) == expected
    raw = (run / "trajectory.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
    rows = json.loads(raw)
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    assert rows[0]["population"] == expected["startingAgents"]
    assert len(rows) <= expected["timesteps"] + 1
    assert all(r["seed"] == expected["seed"] and math.isfinite(r["population"]) and
               0 <= r["population"] <= 2500 and int(r["population"]) == r["population"] for r in rows)
    assert rows[-1]["timestep"] == expected["timesteps"] or rows[-1]["population"] == 0
    zeros = [r["timestep"] for r in rows if r["population"] == 0]
    assert not zeros or all(r["population"] == 0 for r in rows[zeros[0]:])
    nonfinite = [{"timestep": row["timestep"], "field": key} for row in rows for key, value in row.items()
                 if isinstance(value, (int, float)) and not math.isfinite(value)]
    assert nonfinite == record["nonfinite_scalar_fields"]
    assert len(rows) == record["observations"]
    assert rows[-1]["population"] == record["final_population"]
    report.append({"configuration": name, "observations": len(rows), "seed": expected["seed"],
                   "horizon": expected["timesteps"], "extinction_step": zeros[0] if zeros else None,
                   "final_population": rows[-1]["population"], "nonfinite_scalar_fields": nonfinite,
                   "trajectory_sha256": record["trajectory_sha256"]})
args.output.mkdir(parents=True, exist_ok=False)
result = {"scope": "Operational coverage only; no paper-level verdict", "runs": len(report),
          "observations": sum(r["observations"] for r in report), "results": report}
(args.output / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "results"}))
