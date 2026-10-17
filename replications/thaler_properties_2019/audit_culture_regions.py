"""Measure final culture composition in connected high-sugar regions; exploratory only."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("readback", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads(args.protocol.read_text())
results = []
ledger_hashes = {}
regions = {}
for variant in ["original", "corrected"]:
    seen = set()
    for segment in ["retained", "remaining"]:
        root = args.readback / f"{variant}-{segment}" / variant
        raw = (root / "completed.jsonl").read_bytes()
        ledger_hashes[f"{variant}-{segment}"] = hashlib.sha256(raw).hexdigest()
        records = [json.loads(line) for line in raw.splitlines()]
        records = [record for record in records if record["scenario"] == "culture"]
        expected = list(range(33)) if segment == "retained" else list(range(33, 100))
        assert [record["index"] for record in records] == expected
        for record in records:
            index = record["index"]
            assert index not in seen
            seen.add(index)
            assert record["variant"] == variant and record["scenario"] == "culture"
            assert (
                record["seed"] == protocol["seeds"][index] and record["steps"] == 2700
            )
            folder = root / "culture" / f"{index:03d}-{record['seed']}"
            tables = {}
            for kind in ["agents", "cells", "summary"]:
                name = f"trajectory.{kind}.csv"
                packed = (folder / (name + ".gz")).read_bytes()
                assert (
                    hashlib.sha256(packed).hexdigest()
                    == record["files_sha256"][name + ".gz"]
                )
                data = gzip.decompress(packed)
                assert hashlib.sha256(data).hexdigest() == record["files_sha256"][name]
                tables[kind] = list(csv.DictReader(io.StringIO(data.decode())))
            agents = [row for row in tables["agents"] if int(row["time"]) == 2700]
            assert len({row["id"] for row in agents}) == len(agents)
            summary = tables["summary"][-1]
            assert int(summary["time"]) == 2700 and len(agents) == int(
                summary["population"]
            )
            red = sum(int(row["tribe"]) for row in agents)
            assert all(row["tribe"] in ["0", "1"] for row in agents)
            assert red == int(summary["red"]) and len(agents) - red == int(
                summary["blue"]
            )
            maps = {}
            for time in [0, 2700]:
                cells = [row for row in tables["cells"] if int(row["time"]) == time]
                maps[time] = {
                    (int(row["x"]), int(row["y"])): float(row["sugar_capacity"])
                    for row in cells
                }
                assert (
                    len(cells)
                    == len(maps[time])
                    == (2551 if variant == "original" else 2601)
                )
            changed_coordinates = set(maps[0]).symmetric_difference(maps[2700])
            assert all(x in [0, 50] for x, y in changed_coordinates)
            assert all(
                maps[0][position] == maps[2700][position]
                for position in set(maps[0]).intersection(maps[2700])
            )
            if variant == "corrected":
                assert not changed_coordinates
            assert {p: c for p, c in maps[0].items() if c >= 3} == {
                p: c for p, c in maps[2700].items() if c >= 3
            }
            measured = []
            for cutoff in [3, 4]:
                pending = {
                    position
                    for position, capacity in maps[0].items()
                    if capacity >= cutoff
                }
                components = []
                while pending:
                    component = {min(pending)}
                    pending -= component
                    queue = list(component)
                    while queue:
                        x, y = queue.pop()
                        for neighbour in [
                            (x - 1, y),
                            (x + 1, y),
                            (x, y - 1),
                            (x, y + 1),
                        ]:
                            if neighbour in pending:
                                pending.remove(neighbour)
                                component.add(neighbour)
                                queue.append(neighbour)
                    components.append(component)
                assert len(components) == 2
                assert [len(component) for component in components] == (
                    [276, 276] if cutoff == 3 else [69, 69]
                )
                geometry = [sorted(component) for component in components]
                if cutoff not in regions:
                    regions[cutoff] = geometry
                assert geometry == regions[cutoff], (
                    "Region geometry differs between trajectories"
                )
                composition = []
                for component in components:
                    residents = [
                        row
                        for row in agents
                        if (int(row["x"]), int(row["y"])) in component
                    ]
                    assert residents
                    regional_red = sum(int(row["tribe"]) for row in residents)
                    composition.append(
                        {
                            "population": len(residents),
                            "red": regional_red,
                            "blue": len(residents) - regional_red,
                            "red_fraction": regional_red / len(residents),
                        }
                    )
                fractions = [row["red_fraction"] for row in composition]
                measured.append(
                    {
                        "minimum_capacity": cutoff,
                        "regions": composition,
                        "opposite_majorities": (fractions[0] < 0.5 < fractions[1])
                        or (fractions[1] < 0.5 < fractions[0]),
                        "both_at_least_95_percent_one_culture": all(
                            value <= 0.05 or value >= 0.95 for value in fractions
                        ),
                    }
                )
            results.append(
                {
                    "variant": variant,
                    "index": index,
                    "seed": record["seed"],
                    "population": len(agents),
                    "boundary_coordinate_symmetric_difference": len(
                        changed_coordinates
                    ),
                    "global_red_fraction": red / len(agents),
                    "global_45_to_55_percent": 0.45 <= red / len(agents) <= 0.55,
                    "regional_composition": measured,
                }
            )
    assert seen == set(range(100))
summaries = []
for variant in ["original", "corrected"]:
    cohort = [row for row in results if row["variant"] == variant]
    for position, cutoff in enumerate([3, 4]):
        balanced = [row for row in cohort if row["global_45_to_55_percent"]]
        summaries.append(
            {
                "variant": variant,
                "minimum_capacity": cutoff,
                "runs": len(cohort),
                "global_balanced_runs": len(balanced),
                "global_balanced_with_opposite_majorities": sum(
                    row["regional_composition"][position]["opposite_majorities"]
                    for row in balanced
                ),
                "global_balanced_with_both_regions_95_percent": sum(
                    row["regional_composition"][position][
                        "both_at_least_95_percent_one_culture"
                    ]
                    for row in balanced
                ),
                "both_regions_95_percent_runs": sum(
                    row["regional_composition"][position][
                        "both_at_least_95_percent_one_culture"
                    ]
                    for row in cohort
                ),
            }
        )
report = {
    "scope": "Exploratory spatial diagnostic. Connected regions use non-wrapping four-neighbour adjacency and capacity >=3 or >=4. These thresholds and local 95% checks are analyst-defined, not paper-specified replication predicates. Original observer retains its documented coordinate/pre-event limitations.",
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "ledger_sha256": ledger_hashes,
    "regions": regions,
    "summaries": summaries,
    "results": results,
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(summaries, indent=2))
