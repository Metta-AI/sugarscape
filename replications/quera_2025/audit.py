import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import sys

root = Path(sys.argv[1])
output = Path(sys.argv[2])
for line in (root / "sha256.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
summaries = []
for seed in range(3):
    with (root / f"seed-{seed}-agents.csv").open() as stream:
        agents = [
            {k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)
        ]
    with (root / f"seed-{seed}-cells.csv").open() as stream:
        cells = [
            {k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)
        ]
    assert len(agents) == 5000 and len(cells) == 31250
    assert all(math.isfinite(v) for r in agents + cells for v in r.values())
    assert [(r["time"], r["agent"]) for r in agents] == [
        (t, a) for t in range(50) for a in range(1, 101)
    ]
    assert [(r["time"], r["x"], r["y"]) for r in cells] == [
        (t, x, y) for t in range(50) for x in range(1, 26) for y in range(1, 26)
    ]
    assert all(r["alive"] in (0, 1) for r in agents)
    assert all(
        r["alive"] == 1
        and 6 <= r["wealth"] <= 25
        and 1 <= r["x"] <= 25
        and 1 <= r["y"] <= 25
        for r in agents[:100]
    )
    capacities = [r["sugar"] for r in cells[:625]]
    assert all(0 <= r["sugar"] <= capacities[i % 625] for i, r in enumerate(cells))
    lag_mismatches = []
    post_metabolism_violations = []
    dead_positive = []
    for i in range(100, len(agents)):
        before = agents[i - 100]
        after = agents[i]
        predicted = before["alive"] * int(before["wealth"] >= 0)
        if predicted != after["alive"]:
            lag_mismatches.append(i)
        if before["alive"] == 1 and after["wealth"] <= 0 and after["alive"] == 1:
            post_metabolism_violations.append(i)
        if before["alive"] == 1 and after["wealth"] > 0 and after["alive"] == 0:
            dead_positive.append(i)
    assert not lag_mismatches
    duplicate_counts = []
    occupancy_mismatches = 0
    for t in range(50):
        state = agents[t * 100 : (t + 1) * 100]
        locations = Counter((r["x"], r["y"]) for r in state if r["alive"] == 1)
        duplicate_counts.append(sum(n - 1 for n in locations.values()))
        for cell in cells[t * 625 : (t + 1) * 625]:
            if cell["occupied"] != locations[(cell["x"], cell["y"])]:
                occupancy_mismatches += 1
    summaries.append(
        {
            "seed": seed,
            "states": 50,
            "transitions": 49,
            "agent_observations": 5000,
            "cell_observations": 31250,
            "final_population": sum(r["alive"] for r in agents[-100:]),
            "initial_duplicate_live_positions": duplicate_counts[0],
            "maximum_duplicate_live_positions": max(duplicate_counts),
            "occupancy_count_mismatches": occupancy_mismatches,
            "old_wealth_survival_mismatches": len(lag_mismatches),
            "post_metabolism_nonpositive_but_alive": len(post_metabolism_violations),
            "positive_after_harvest_but_died": len(dead_positive),
            "first_post_metabolism_violations": [
                agents[i] for i in post_metabolism_violations[:3]
            ],
        }
    )
output.mkdir(exist_ok=False)
(output / "audit.json").write_text(
    json.dumps(
        {
            "seeds": summaries,
            "scope": "Complete native forward-run file integrity and state/survival audit; no independent movement replay, gradient validation, or calibration verdict.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(summaries))
