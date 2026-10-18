"""Compare all 51 timing cells only after independently audited coverage is complete."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("audits", type=Path, nargs="+")
args = parser.parse_args()
assets = Path(__file__).resolve().parents[1]
target_path = assets / "results/archived/paper-timing-comparison.json"
targets = {
    (row["table"], row["variant"], row["index"]): row["paper_seconds"]
    for row in json.loads(target_path.read_text())["rows"]
}
assert len(targets) == 51
observed = {}
input_hashes = {}
for path in args.audits:
    raw = path.read_bytes()
    input_hashes[str(path)] = hashlib.sha256(raw).hexdigest()
    audit = json.loads(raw)
    for row in audit["rows"]:
        if not row["accepted"]:
            continue
        condition = row["condition"]
        table = condition["table"]
        variant = condition["scenario"] if table == 9 else condition["variant"]
        index = condition["agents"] if table == 8 else condition["caps"]
        key = table, variant, index
        assert key in targets
        assert row["r_squared"] >= 0.99
        assert row["ols_seconds"] > 0
        assert len(row["raw_samples"]) == 4
        if key in observed:
            assert observed[key] == row, (key, "conflicting repeated evidence")
        else:
            observed[key] = row
missing = sorted(targets.keys() - observed.keys())
assert not missing, {
    "missing_conditions": missing,
    "accepted": len(observed),
    "required": 51,
}
rows = [
    {
        "table": table,
        "variant": variant,
        "index": index,
        "paper_seconds": targets[table, variant, index],
        "native_seconds": record["ols_seconds"],
        "native_over_paper": record["ols_seconds"] / targets[table, variant, index],
        "r_squared": record["r_squared"],
        "report_sha256": record["report_sha256"],
    }
    for (table, variant, index), record in sorted(observed.items())
]
report = {
    "conditions": len(rows),
    "target_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "input_audit_sha256": input_hashes,
    "rows": rows,
    "limits": [
        "Inputs must first pass the native raw-measurement auditors; this comparison does not replace those audits.",
        "Tables 6 and 8 use different hardware; Table 9 matches instance class but historical clock and isolation remain unknown.",
        "Four iteration-count measurements are not four independent experiment repetitions.",
        "Ratios are descriptive; no new acceptance tolerance, significance test or full-paper verdict is introduced.",
    ],
    "completed_study": False,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({"conditions": len(rows), "completed_study": False}))
