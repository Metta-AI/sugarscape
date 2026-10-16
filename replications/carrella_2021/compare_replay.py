"""Recompute the 150 author-defined statistics for every complete replay in a declared range."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trajectories", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.reference.open() as stream:
        reference = list(csv.DictReader(stream))
    assert 0 <= args.start < args.stop <= len(reference)
    assert {p.name for p in args.trajectories.glob("*.csv")} == {
        f"row-{row}.csv" for row in range(args.start, args.stop)
    }
    args.output.mkdir(parents=True, exist_ok=False)
    comparisons = []
    with (args.output / "summary_statistics.csv").open("x") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reference[0]))
        writer.writeheader()
        for index in range(args.start, args.stop):
            trajectory = args.trajectories / f"row-{index}.csv"
            with trajectory.open() as source:
                reader = csv.DictReader(source)
                names = reader.fieldnames[1:]
                rows = list(reader)
            assert len(rows) == 501
            assert float(rows[0]["tick"]) == 0
            for previous, current in zip(rows, rows[1:]):
                if float(previous["count turtles"]) == 0:
                    assert current == previous, "The extinct author model must remain unchanged"
                else:
                    assert float(current["tick"]) == float(previous["tick"]) + 1
            measured = {}
            for name in names:
                values = np.array([float(row[name]) for row in rows])
                assert np.isfinite(values).all()
                measured.update({
                    "mean_" + name: float(values.mean()),
                    "min_" + name: float(values.min()),
                    "last_" + name: float(values[-1]),
                    "sd_" + name: float(values.std()),
                    "trend_" + name: float(np.polyfit(np.arange(len(values), dtype=float), values, 1)[0]),
                    "max_" + name: float(values.max()),
                })
                for tick in range(25, 500, 25):
                    measured[f"snap_{tick}_{name}"] = float(values[tick])
            assert len(measured) == 150 and measured.keys() == reference[index].keys()
            writer.writerow(measured)
            mismatches = {
                name: {"replayed": value, "archived": float(reference[index][name])}
                for name, value in measured.items()
                if not np.isclose(value, float(reference[index][name]), rtol=1e-10, atol=1e-10)
            }
            comparisons.append({
                "row": index, "observations": len(rows), "matched_statistics": 150 - len(mismatches),
                "mismatches": mismatches,
                "maximum_absolute_error": max(abs(value - float(reference[index][name]))
                                              for name, value in measured.items()),
                "trajectory_sha256": hashlib.sha256(trajectory.read_bytes()).hexdigest(),
            })
    matched = sum(row["matched_statistics"] for row in comparisons)
    total = 150 * len(comparisons)
    report = {
        "start": args.start, "stop": args.stop, "matched_statistics": matched, "total_statistics": total,
        "comparison": "Floating-point replay tolerance: rtol=1e-10, atol=1e-10; not a paper-level equivalence margin.",
        "rows": comparisons,
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in (args.reference, Path(__file__), args.output / "summary_statistics.csv")},
    }
    with (args.output / "comparison.json").open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"Rows {args.start}..{args.stop - 1}: {matched}/{total} archived statistics matched")
    if matched != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
