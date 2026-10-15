"""Recompute all 150 author-defined statistics from a complete NetLogo replay."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trajectory", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--row", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.trajectory.open() as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames[1:]
        rows = list(reader)
    assert len(rows) == 501
    assert [float(row["tick"]) for row in rows] == list(range(501))
    with args.reference.open() as stream:
        reference = list(csv.DictReader(stream))[args.row]
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
    assert len(measured) == 150 and measured.keys() == reference.keys()
    differences = {name: {"replayed": value, "archived": float(reference[name]),
                           "absolute_error": abs(value - float(reference[name]))}
                   for name, value in measured.items()}
    mismatches = [name for name, value in measured.items()
                  if not np.isclose(value, float(reference[name]), rtol=1e-10, atol=1e-10)]
    report = {
        "row": args.row, "observations": len(rows), "matched_statistics": 150 - len(mismatches),
        "mismatches": mismatches, "differences": differences,
        "comparison": "Floating-point replay tolerance: rtol=1e-10, atol=1e-10; not a paper-level equivalence margin.",
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in (args.trajectory, args.reference, Path(__file__))},
    }
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"Row {args.row}: {150 - len(mismatches)}/150 archived statistics matched")


if __name__ == "__main__":
    main()
