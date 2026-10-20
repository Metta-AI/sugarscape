"""Audit the completed native rerun against the preserved timed-out attempt."""
from pathlib import Path
import gzip
import hashlib
import json
import math

root = Path(__file__).resolve().parent
inventory = json.loads((root / "inventory.json").read_bytes())
failed = inventory["failed_attempts"][0]
assert (failed["seed"], failed["condition"]) == (19522, "trade_basic")
old = Path(failed["directory"])
run = root / "seed-19522/trade_basic"
receipt = json.loads((run / "exit.json").read_bytes())
validated = json.loads((run / "validated.json").read_bytes())
assert receipt["exit_code"] == 0
assert not (old / "exit.json").exists()
raw = (run / "trajectory.json").read_bytes()
assert raw == (old / "trajectory.json").read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == failed["saved_trajectory_sha256"] == validated["trajectory_sha256"]
manifest = json.loads((run / "manifest.json").read_bytes())
previous_manifest = json.loads((old / "manifest.json").read_bytes())
assert manifest == previous_manifest
engine = root.parent.parent / "sugarscape-dtl-replacing-reference"
for name, value in manifest["source_sha256"].items():
    assert hashlib.sha256((engine / name).read_bytes()).hexdigest() == value
config = json.loads((run / "effective-config.json").read_bytes())
previous_config = json.loads((old / "effective-config.json").read_bytes())
assert {k: v for k, v in config.items() if k != "logfile"} == {
    k: v for k, v in previous_config.items() if k != "logfile"
}
assert config["seed"] == 19522 and config["timesteps"] == 10000
prior = root.parent.parent / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15/seed-19522/trade_basic"
prefix = [json.loads(line) for line in (run / "original-schedule.jsonl").read_text().splitlines()]
assert prefix == json.loads(gzip.decompress((prior / "trajectory.json.gz").read_bytes()))
assert len(prefix) == 501
rows = json.loads(raw)
assert len(rows) == 10001
for time, row in enumerate(rows):
    assert row["timestep"] == time and row["seed"] == 19522
    assert 0 <= row["population"] <= 2500 and int(row["population"]) == row["population"]
    assert all(math.isfinite(x) for value in row.values() for x in (value if isinstance(value, list) else [value]))
report = {
    "seed": 19522, "condition": "trade_basic", "native_exit_code": 0,
    "observations": len(rows), "original_prefix_records_exact": len(prefix),
    "failed_attempt_full_trajectory_byte_identical": True,
    "source_and_effective_settings_unchanged": True,
    "elapsed_seconds": receipt["elapsed_seconds"],
    "trajectory_sha256": digest,
    "final_population": rows[-1]["population"],
    "scope": "Successful native recovery with identical retained outputs; timeout cause is not isolated. No full-ensemble or paper-completion claim.",
}
output = root / "recovered-attempt-audit.json"
assert not output.exists()
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
