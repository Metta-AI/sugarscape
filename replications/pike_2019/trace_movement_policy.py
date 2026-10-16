"""Passively observe the released high-focus movement policy's selected holdings."""

import argparse
import json
import runpy
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("approach", choices=["explicit", "network"])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (
    args.engine.resolve()
    / {"explicit": "Policy-Explicit", "network": "Policy-Network"}[args.approach]
)
sys.path[:0] = [str(source), str(args.library.resolve())]
import NetAgent
import organization

args.output.mkdir(parents=True, exist_ok=False)
stream = (args.output / "high-focus.jsonl").open("x")
active = []
native_high = organization.rules.step_high
native_move = NetAgent.NetAgent.move


def observed_high(self, agent, meta):
    assert not active
    members = [
        {
            "id": member.unique_id,
            "sugar": float(member.accumulations[1]),
            "spice": float(member.accumulations[2]),
        }
        for member in meta.sub_agents.values()
    ]
    active.append((agent, meta, members))
    native_high(self, agent, meta)
    active.pop()


def observed_move(self):
    if active:
        actor, group, members = active[0]
        assert actor is self
        stream.write(
            json.dumps(
                {
                    "step": self.model.step_num,
                    "actor": self.unique_id,
                    "group": group.unique_id,
                    "members_before_policy": members,
                    "perceived_sugar": float(self.accumulations[1]),
                    "perceived_spice": float(self.accumulations[2]),
                },
                allow_nan=False,
            )
            + "\n"
        )
    return native_move(self)


organization.rules.step_high = observed_high
NetAgent.NetAgent.move = observed_move
runner = Path(__file__).with_name("run_groups.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.approach,
    "10",
    "movement",
    str(args.seed),
    str(args.output / "configured"),
]
runpy.run_path(str(runner), run_name="__main__")
stream.close()
