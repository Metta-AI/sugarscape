"""Fetch pinned author artifacts and audit the complete Sugarscape reference table."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import urllib.request

REVISION = "0400f750063215d06659a203f777b21da2e99231"
FILES = (
    "LICENSE.txt", "setup.R", "sugarscape.Rmd", "sugarscape_small.Rmd",
    "data/sugarscape/Sugarscape trade.nlogo", "data/sugarscape/sugarscape.py",
    "data/sugarscape/params_sugarscape.csv", "data/sugarscape/sugarscape.csv",
)
BOUNDS = ((1, 100000), (100, 500), (0, .2), (6, 80), (6, 80), (20, 100))
PARAMETERS = ("random-seed", "initial-population", "pmut", "maximum-sugar-endowment",
              "maximum-spice-endowment", "wealth-reproduction")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in FILES:
        target = args.output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        url = "https://raw.githubusercontent.com/CarrKnight/nofreelunch/" + REVISION + "/" + name.replace(" ", "%20")
        with urllib.request.urlopen(url) as response:
            target.write_bytes(response.read())
        hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    with (args.output / "data/sugarscape/params_sugarscape.csv").open() as stream:
        reader = csv.DictReader(stream)
        assert tuple(reader.fieldnames) == PARAMETERS
        parameters = list(reader)
    with (args.output / "data/sugarscape/sugarscape.csv").open() as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames
        assert len(names) == len(set(names)) == 150
        outputs = list(reader)
    assert len(parameters) == len(outputs) == 5000
    for row in parameters:
        for name, (low, high) in zip(PARAMETERS, BOUNDS):
            value = float(row[name])
            assert math.isfinite(value) and low <= value <= high
    for row in outputs:
        assert all(math.isfinite(float(value)) for value in row.values())
    constants = [name for name in names if len({row[name] for row in outputs}) == 1]
    report = {
        "source_repository": "https://github.com/CarrKnight/nofreelunch",
        "revision": REVISION, "sha256": hashes,
        "rows": len(outputs), "parameters_including_seed": len(PARAMETERS),
        "summary_statistics": len(names), "constant_columns": constants,
        "parameter_ranges": {name: [min(float(row[name]) for row in parameters),
                                    max(float(row[name]) for row in parameters)] for name in PARAMETERS},
        "status": "Source-artifact audit only; no simulation or calibration replication completed.",
    }
    (args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
