"""Run a separately labeled shared-balance correction with every-step resource accounting."""

import argparse
import csv
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("variant", choices=["common-one", "common-multi"])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert os.environ["PYTHONHASHSEED"] == "0"
for root, revision in [
    (args.engine, "585e53398f4f58e89ec184c83bb20819f0e4c96a"),
    (args.library, "99d2091721076df9fff32e8b49a0e33e98c34a6f"),
]:
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        == revision
    )
    assert not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, text=True
    ).strip()
source = (
    args.engine.resolve()
    / {
        "common-one": "Common Resource- one level",
        "common-multi": "Common Resource- multi-level",
    }[args.variant]
)
sys.path.insert(0, str(args.library.resolve()))
sys.path.insert(0, str(source))
import NetAgent as N
import ResourceScape as R
import shared_pool
from NetScape import NetScape

out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
(out / "manifest.json").write_text(
    json.dumps(
        {
            "variant": args.variant,
            "numpy_seed": args.seed,
            "policy_seed": args.seed,
            "mesa_seed": 42,
            "pythonhashseed": "0",
            "steps": 1000,
            "correction_sha256": hashlib.sha256(
                Path(shared_pool.__file__).read_bytes()
            ).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "native_source_sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.glob("*.py")
            },
            "scope": "Corrective experiment, not the unchanged author model or a paper replication verdict.",
        },
        indent=2,
    )
    + "\n"
)


def living_totals(model):
    balances = {
        id(a.accumulations): a.accumulations
        for a in model.ml.agents_by_type[N.NetAgent].values()
    }
    return [math.fsum(float(b[k]) for b in balances.values()) for k in [1, 2]]


growth, metabolism, death_loss = [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]
native_grow, native_eat, native_die = R.resource.step, N.NetAgent.eat, N.NetAgent.die


def measured_grow(self):
    before = [self.value_sug, self.value_spice]
    native_grow(self)
    for i, after in enumerate([self.value_sug, self.value_spice]):
        growth[i] += after - before[i]


def measured_eat(self):
    before = [self.accumulations[k] for k in [1, 2]]
    native_eat(self)
    for i, key in enumerate([1, 2]):
        consumed = before[i] - self.accumulations[key]
        assert math.isclose(
            consumed, self.metabolism[["sug_bolism", "spice_bolism"][i]], abs_tol=1e-8
        )
        metabolism[i] += consumed


def measured_die(self):
    before = living_totals(self.model)
    native_die(self)
    after = living_totals(self.model)
    for i in range(2):
        death_loss[i] += before[i] - after[i]


R.resource.step, N.NetAgent.eat, N.NetAgent.die = (
    measured_grow,
    measured_eat,
    measured_die,
)
np.random.seed(args.seed)
random.seed(args.seed)
model = NetScape(seed=42)
with (out / "accounting.csv").open("x", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        [
            "step",
            "commodity",
            "population",
            "before",
            "after",
            "growth",
            "metabolism",
            "death_loss",
            "error",
        ]
    )
    for step in range(1, 1001):
        before = living_totals(model)
        resources = model.ml.agents_by_type[R.resource].values()
        before = [
            before[0] + math.fsum(r.value_sug for r in resources),
            before[1] + math.fsum(r.value_spice for r in resources),
        ]
        growth[:] = metabolism[:] = death_loss[:] = [0.0, 0.0]
        model.step()
        after = living_totals(model)
        resources = model.ml.agents_by_type[R.resource].values()
        after = [
            after[0] + math.fsum(r.value_sug for r in resources),
            after[1] + math.fsum(r.value_spice for r in resources),
        ]
        for i, commodity in enumerate(["sugar", "spice"]):
            error = after[i] - before[i] - growth[i] + metabolism[i] + death_loss[i]
            writer.writerow(
                [
                    step,
                    commodity,
                    len(model.ml.agents_by_type[N.NetAgent]),
                    before[i],
                    after[i],
                    growth[i],
                    metabolism[i],
                    death_loss[i],
                    error,
                ]
            )
            stream.flush()
            assert all(math.isfinite(v) for v in [before[i], after[i], error])
            assert abs(error) < 1e-7, (step, commodity, error)
(model.datacollector.get_table_dataframe("Health")).to_csv(
    out / "health.csv", index=False
)
(out / "prices.json").write_text(json.dumps(model.price_record, allow_nan=False))
(out / "complete.json").write_text(
    json.dumps(
        {"steps": 1000, "individual_agents": len(model.ml.agents_by_type[N.NetAgent])}
    )
    + "\n"
)
