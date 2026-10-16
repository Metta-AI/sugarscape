"""Passively trace debt creation and recovery in the corrective experiment."""

import argparse
import json
import runpy
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("variant", choices=["common-one", "common-multi"])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (
    args.engine.resolve()
    / {
        "common-one": "Common Resource- one level",
        "common-multi": "Common Resource- multi-level",
    }[args.variant]
)
sys.path[:0] = [str(source), str(args.library.resolve())]
import NetAgent

args.output.mkdir(parents=True, exist_ok=False)
stream = (args.output / "events.jsonl").open("x")
native_eat = NetAgent.NetAgent.eat
native_collect = NetAgent.NetAgent.collect


def balances(agent):
    return [float(agent.accumulations[key]) for key in [1, 2]]


def record(agent, event, before, after):
    stream.write(
        json.dumps(
            {
                "event": event,
                "step": agent.model.step_num,
                "agent": agent.unique_id,
                "status": agent.status,
                "before": before,
                "after": after,
                "shared_members": [
                    member.unique_id
                    for member in agent.model.ml.agents_by_type[
                        NetAgent.NetAgent
                    ].values()
                    if member.accumulations is agent.accumulations
                ],
            },
            allow_nan=False,
        )
        + "\n"
    )
    stream.flush()


def traced_eat(self):
    before = balances(self)
    native_eat(self)
    after = balances(self)
    if min(after) < 0:
        record(self, "negative_after_metabolism", before, after)


def traced_collect(self):
    before = balances(self)
    native_collect(self)
    after = balances(self)
    if min(before) < 0:
        record(self, "harvest_with_existing_debt", before, after)


NetAgent.NetAgent.eat = traced_eat
NetAgent.NetAgent.collect = traced_collect
runner = Path(__file__).with_name("run_corrected.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.variant,
    str(args.seed),
    str(args.output / "run"),
]
runpy.run_path(str(runner), run_name="__main__")
stream.close()
