from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import sys

import numpy as np

root = Path(__file__).resolve().parent
repo = Path(sys.argv[1])
protocol = json.loads((root / "protocol.json").read_bytes())
audit_path = Path(sys.argv[2])
audit = json.loads(audit_path.read_bytes())
lookup = {row["run_id"]: row for row in audit["completed"]}
assert len(lookup) == 1600
cohorts = ["rule-m-rule-m", "ec-ec", "q-q", "sarsa-sarsa"]
records = []
pins = {}
endpoint_rows = []
source_files = {}
for pair, name in zip(protocol["pair_indices"], cohorts, strict=True):
    folder = repo / "results" / protocol["cohort_folders"][protocol["pair_indices"].index(pair)]
    summary = json.loads((folder / "cohort-summary.json").read_bytes())
    assert (
        summary["pair_index"] == pair and summary["interpretation"] == "paper-table"
    )
    assert summary["runs"] == 50
    assert summary["group_A"] == summary["group_B"]
    field_map = {
        metric: {breed: f"mean [{metric}] of group-{breed}" for breed in ["A", "B"]}
        for metric in ["sugar", "vision", "metabolism", "age"]
    }
    field_map.update(
        {
            "combat": {"A": "combat-agent-a-die", "B": "combat-agent-b-die"},
            "starvation": {"A": "starve-agent-a-die", "B": "starve-agent-b-die"},
            "max_age": {"A": "max [age] of group-A", "B": "max [age] of group-B"},
        }
    )
    fields = [
        field_map[metric][breed]
        for metric in protocol["metrics"]
        for breed in ["A", "B"]
    ]
    endpoints = []
    for repeat in range(50):
        run_id = f"paper-table-pair-{pair:02d}-repeat-{repeat:02d}"
        row = lookup[run_id]
        raw = (Path(row["directory"]) / "trajectory.csv").read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert (
            digest == row["trajectory_sha256"] == summary["trajectory_sha256"][run_id]
        )
        lines = raw.splitlines()
        assert len(lines) == 20002
        end = next(
            csv.DictReader(io.StringIO((lines[0] + b"\n" + lines[-1] + b"\n").decode()))
        )
        assert int(end["tick"]) == 20000
        values = [float(end[field]) for field in fields]
        assert np.isfinite(values).all()
        endpoints.append(values)
        endpoint_rows.append([pair, run_id, *values])
        pins[run_id] = digest
    matrix = np.array(endpoints)
    index_raw = gzip.decompress((folder / "bootstrap-indices.u8.gz").read_bytes())
    assert (
        hashlib.sha256(index_raw).hexdigest() == summary["bootstrap"]["indices_sha256"]
    )
    indices = np.frombuffer(index_raw, dtype=np.uint8).reshape(20000, 50)
    assert indices.max() < 50
    for filename in ["cohort-summary.json", "bootstrap-indices.u8.gz"]:
        source_files[str(folder / filename)] = hashlib.sha256(
            (folder / filename).read_bytes()
        ).hexdigest()
    for j, metric in enumerate(protocol["metrics"]):
        differences = matrix[:, 2 * j] - matrix[:, 2 * j + 1]
        draws = differences[indices].mean(axis=1)
        interval = np.quantile(draws, [0.025, 0.975], method="linear")
        records.append(
            {
                "pair_index": pair,
                "pairing": name,
                "method": summary["group_A"],
                "metric": metric,
                "A_endpoint_mean": float(matrix[:, 2 * j].mean()),
                "B_endpoint_mean": float(matrix[:, 2 * j + 1].mean()),
                "paired_endpoint_mean": float(differences.mean()),
                "paired_endpoint_sample_sd": float(differences.std(ddof=1)),
                "pointwise_bootstrap_interval_95": interval.tolist(),
                "endpoint_positive_runs": int((differences > 0).sum()),
                "endpoint_equal_runs": int((differences == 0).sum()),
                "endpoint_negative_runs": int((differences < 0).sum()),
            }
        )
with (root / "paired-endpoints.csv").open("w") as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        ["pair_index", "run_id"]
        + [f"{metric}_{role}" for metric in protocol["metrics"] for role in ["A", "B"]]
    )
    writer.writerows(endpoint_rows)
assert len(pins) == 200 and len(records) == 28
report = {
    "inputs": 200,
    "contrasts": 28,
    "raw_trajectory_sha256": pins,
    "source_files_sha256": source_files,
    "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
    "records": records,
    "scope": protocol["scope"],
}
(root / "contrasts.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(records, indent=2))
