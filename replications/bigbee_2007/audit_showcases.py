"""Audit execution/repeatability and expose invalid native measurement records."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.batch / "manifest.json").read_text())
completed = [json.loads(line) for line in (args.batch / "completed.jsonl").read_text().splitlines()]
assert [(r["target"], r["repetition"]) for r in completed] == [(t["id"], n) for t in manifest["targets"] for n in [1, 2]]
assert all(r["exit_code"] == 0 for r in completed)
reports = []
for index, target in enumerate(manifest["targets"]):
    first = (args.batch / f'{target["id"]}-repeat1.csv').read_bytes()
    second = (args.batch / f'{target["id"]}-repeat2.csv').read_bytes()
    assert first == second
    assert hashlib.sha256(first).hexdigest() == completed[index * 2]["stdout_sha256"] == completed[index * 2 + 1]["stdout_sha256"]
    rows = list(csv.reader(first.decode().splitlines()))
    header = rows.pop(0)
    assert header[:8] == ["run", "time", "gini", "agents_born", "alive_agents", "avg_vision", "avg_metabolism_sugar", "avg_metabolism_spice"]
    config_path = Path(manifest["engine"]) / target["configuration"]
    assert hashlib.sha256(config_path.read_bytes()).hexdigest() == target["configuration_sha256"]
    settings = dict(line.split("=", 1) for line in config_path.read_text().splitlines() if "=" in line and not line.lstrip().startswith("#"))
    settings = {k.strip(): v.strip() for k, v in settings.items()}
    rate = int(settings["stats_rate"])
    assert [float(row[1]) for row in rows] == [0, *range(rate, manifest["horizon"] + 2, rate)]
    if "agents_file" in settings:
        locations = (Path(manifest["engine"]) / settings["agents_file"]).read_text()
        initial_population = sum(character not in {"0", "\n", "\r"} for character in locations)
    else:
        initial_population = int(settings["num_agents"])
    assert int(rows[0][4]) == initial_population
    invalid = []
    for row in rows:
        assert len(row) >= 8 and int(row[0]) == 1 and 0 <= int(row[4]) <= 2500
        for column, value in zip(header[:8], row[:8], strict=True):
            if value in {"NaN", "∞", "-∞"} or not math.isfinite(float(value)):
                invalid.append({"time": float(row[1]), "column": column, "value": value})
    reports.append({"target": target["id"], "observations_each": len(rows), "byte_identical": True,
                    "final_population": int(rows[-1][4]), "nonfinite_core_metrics": len(invalid),
                    "first_nonfinite_core_metrics": invalid[:5],
                    "rows_with_header_width_mismatch": sum(len(row) != len(header) for row in rows)})
report = {"runs": len(completed), "paired_configurations": len(reports),
          "observations_total": 2 * sum(r["observations_each"] for r in reports), "results": reports,
          "interpretation": "All native executions completed and paired logs agree. Nonfinite metrics and malformed column schemas are explicitly reported, not accepted as valid scientific measurements. No paper replication verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
