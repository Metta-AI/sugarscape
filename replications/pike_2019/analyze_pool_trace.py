"""Verify repeated contributions in a byte-identical native shared-pool trace."""

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("trace", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
subprocess.run(
    [
        sys.executable,
        str(Path(__file__).with_name("diagnose_resources.py")),
        str(args.native),
        str(args.trace),
        str(args.output),
    ],
    check=True,
)
rows = [
    json.loads(line)
    for line in (args.trace / "pool-calls.jsonl").read_text().splitlines()
]
assert len(rows) == 150
# JSON records integer and floating commodity keys differently; normalize their numeric meaning.
for row in rows:
    row["returned_pool"] = {float(k): float(v) for k, v in row["returned_pool"].items()}
    for member in row["members"]:
        member["holdings"] = {float(k): float(v) for k, v in member["holdings"].items()}
    for key in [1.0, 2.0]:
        assert math.isclose(
            row["returned_pool"][key],
            sum(m["holdings"][key] for m in row["members"]),
            rel_tol=1e-12,
        )
first, second = rows[:2]
assert first["step"] == second["step"] == 6
assert first["group_id"] == second["group_id"] == "trades_10_0"
assert first["cached_pool"] is None
assert (
    [m["id"] for m in first["members"]]
    == [m["id"] for m in second["members"]]
    == [100, 108]
)
cached = {float(k): float(v) for k, v in second["cached_pool"].items()}
repeated = first["members"][0]["holdings"]
assert repeated == second["members"][0]["holdings"]
assert second["members"][1]["holdings"] == cached
for key in [1.0, 2.0]:
    assert math.isclose(
        second["returned_pool"][key] - cached[key], repeated[key], rel_tol=1e-12
    )
report = {
    "verified_calls": 150,
    "verified_commodity_sums": 300,
    "step": 6,
    "group": first["group_id"],
    "unchanged_members": [100, 108],
    "initial_pool": first["returned_pool"],
    "pool_after_first_agent_acts": cached,
    "unchanged_holdings_counted_again": repeated,
    "next_calculated_pool": second["returned_pool"],
    "interpretation": "Both initial holdings enter the first pool. After one member acts, its holdings contain the current pool, while the other retains its original contribution. The next native calculation adds that original contribution to the current pool again. Distinct dictionaries therefore double-count resources without object aliasing. Full native outputs remain byte-identical and numerically invalid.",
}
(args.output / "accounting-proof.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(json.dumps(report))
