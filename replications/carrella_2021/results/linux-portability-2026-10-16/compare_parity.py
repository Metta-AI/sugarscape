"""Compare every saved observation and summary from eight Linux portability replays."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("remote", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = Path("/Users/relh/Code/workspace/sugarscape-replication-evidence")
expected_indices = [0, 100, 500, 507, 630, 2005, 2138, 3630]
assert (
    json.loads((args.remote / "parity-complete.json").read_text())["completed"]
    == expected_indices
)
assert json.loads((args.remote / "parity-terminal.json").read_text())["exit_code"] == 0
reports = []
for index in expected_indices:
    if index < 507:
        local = root / "carrella-independent-5000-001"
    elif index < 631:
        local = root / "carrella-independent-shard-1-001"
    elif index < 2139:
        local = root / "carrella-independent-shard-2-001"
    else:
        local = root / "carrella-independent-shard-3-001"
    remote = args.remote / f"parity-{index}"
    lm = json.loads((local / "manifest.json").read_text())
    rm = json.loads((remote / "manifest.json").read_text())
    for key in (
        "source_sha256",
        "parameter_sha256",
        "reference_sha256",
        "python",
        "numpy",
        "pydantic",
    ):
        assert lm[key] == rm[key], (index, key)
    assert (rm["start"], rm["stop"]) == (index, index + 1)
    raw_local = gzip.decompress((local / f"row-{index}.csv.gz").read_bytes())
    raw_remote = gzip.decompress((remote / f"row-{index}.csv.gz").read_bytes())
    local_rows = list(csv.DictReader(io.StringIO(raw_local.decode())))
    remote_rows = list(csv.DictReader(io.StringIO(raw_remote.decode())))
    assert len(local_rows) == len(remote_rows) == 501
    trajectory_errors = {}
    for key in local_rows[0]:
        differences = [
            abs(float(a[key]) - float(b[key])) for a, b in zip(local_rows, remote_rows)
        ]
        trajectory_errors[key] = {
            "different": sum(d != 0 for d in differences),
            "max_error": max(differences),
        }
    lr = next(
        json.loads(line)
        for line in (local / "completed.jsonl").read_text().splitlines()
        if json.loads(line)["row"] == index
    )
    rr = json.loads((remote / "completed.jsonl").read_text())
    assert rr["row"] == index
    assert hashlib.sha256(raw_local).hexdigest() == lr["trajectory_sha256"]
    assert hashlib.sha256(raw_remote).hexdigest() == rr["trajectory_sha256"]
    local_summary = list(csv.DictReader((local / "summary_statistics.csv").open()))[
        index - lm["start"]
    ]
    remote_summary = list(csv.DictReader((remote / "summary_statistics.csv").open()))
    assert len(remote_summary) == 1 and len(local_summary) == 150
    errors = {
        k: abs(float(local_summary[k]) - float(remote_summary[0][k]))
        for k in local_summary
    }
    reports.append(
        {
            "index": index,
            "trajectory_bytes_exact": raw_local == raw_remote,
            "trajectory_errors": trajectory_errors,
            "observations": len(list(csv.DictReader(io.StringIO(raw_local.decode())))),
            "exact_statistics": sum(e == 0 for e in errors.values()),
            "maximum_summary_error": max(errors.values()),
            "summary_errors": {k: v for k, v in errors.items() if v != 0},
        }
    )
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(
    json.dumps(
        {
            "results": reports,
            "scope": "Eight selected completed inputs only; no claim of universal platform equivalence.",
        },
        indent=2,
    )
    + "\n"
)
print(
    json.dumps([{k: v for k, v in r.items() if k != "summary_errors"} for r in reports])
)
