"""Replay a completed independent input and expose its raw transaction prices."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from model import Model, Parameters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("ensemble", type=Path)
parser.add_argument("row", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.ensemble / "manifest.json").read_text())
assert (
    hashlib.sha256(Path(__file__).with_name("model.py").read_bytes()).hexdigest()
    == manifest["source_sha256"]["model.py"]
)
records = [
    json.loads(line)
    for line in (args.ensemble / "completed.jsonl").read_text().splitlines()
]
record = next(record for record in records if record["row"] == args.row)
raw = (args.ensemble / f"row-{args.row}.csv").read_bytes()
assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
reference = list(csv.reader(raw.decode().splitlines()))[1:]
assert len(reference) == 501
model = Model(Parameters(**record["parameters"]))
args.output.mkdir(parents=True, exist_ok=False)
previous_price = 0.0
with (args.output / "prices.jsonl").open("x") as stream:
    for index, expected in enumerate(reference):
        observed = model.observation()
        assert observed == [float(value) for value in expected], index
        assert len(model.prices) == observed[5]
        assert all(math.isfinite(price) and price > 0 for price in model.prices)
        if model.prices:
            assert sum(model.prices) / len(model.prices) == observed[6]
        else:
            assert observed[6] == previous_price
        stream.write(
            json.dumps(
                {
                    "observation": index,
                    "tick": model.tick,
                    "population": observed[1],
                    "prices": model.prices,
                    "mean_price": observed[6],
                },
                allow_nan=False,
            )
            + "\n"
        )
        previous_price = observed[6]
        model.step()
report = {
    "row": args.row,
    "observations": 501,
    "matched_values": 3507,
    "trajectory_sha256": record["trajectory_sha256"],
    "model_sha256": manifest["source_sha256"]["model.py"],
    "trace_sha256": hashlib.sha256(
        (args.output / "prices.jsonl").read_bytes()
    ).hexdigest(),
    "scope": "Exact independent-model replay and transaction/mean-price accounting; not native RNG equivalence.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
